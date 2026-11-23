<?php
declare(strict_types=1);

// Endpoint lokal: konfigurasi hanya melalui environment proses PHP.
ini_set('display_errors', '0');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
header('Cross-Origin-Resource-Policy: same-origin');

function respond(int $status, array $body): never {
    http_response_code($status);
    echo json_encode($body, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
    exit;
}

if (!in_array($_SERVER['REMOTE_ADDR'] ?? '', ['127.0.0.1', '::1'], true)) {
    respond(403, ['error' => 'API hanya tersedia dari komputer lokal.']);
}
$hostHeader = $_SERVER['HTTP_HOST'] ?? '';
if (!preg_match('/^(localhost|127\.0\.0\.1|\[::1\])(:[0-9]{1,5})?$/iD', $hostHeader)) {
    respond(403, ['error' => 'Host tidak diizinkan.']);
}
if (($_SERVER['HTTP_SEC_FETCH_SITE'] ?? '') === 'cross-site') {
    respond(403, ['error' => 'Permintaan lintas situs tidak diizinkan.']);
}
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'GET') {
    header('Allow: GET');
    respond(405, ['error' => 'Gunakan GET.']);
}
if (array_diff(array_keys($_GET), ['health']) || (isset($_GET['health']) && $_GET['health'] !== '1')) {
    respond(400, ['error' => 'Parameter tidak valid.']);
}

function envRequired(string $name): string {
    $value = getenv($name);
    if ($value === false || $value === '') { throw new RuntimeException('Configuration unavailable'); }
    return $value;
}

function scaled(string $value): int {
    if (!preg_match('/^(-?)([0-9]+)(?:\.([0-9]{1,4}))?$/D', $value, $matches)) {
        throw new RuntimeException('Invalid decimal');
    }
    $number = (int)$matches[2] * 10000 + (int)str_pad($matches[3] ?? '', 4, '0');
    if ($number > 9007199254740991) { throw new RuntimeException('Unsafe numeric range'); }
    return ($matches[1] === '-' ? -1 : 1) * $number;
}

try {
    $host = envRequired('DW_HOST');
    $port = envRequired('DW_PORT');
    $database = envRequired('DW_DATABASE');
    if (!in_array($host, ['localhost', '127.0.0.1', '::1'], true)
        || !ctype_digit($port) || (int)$port < 1 || (int)$port > 65535
        || !preg_match('/^[a-zA-Z0-9_]+$/D', $database)) {
        throw new RuntimeException('Invalid configuration');
    }
    $pdo = new PDO("mysql:host=$host;port=$port;dbname=$database;charset=utf8mb4", envRequired('DW_USER'), envRequired('DW_PASSWORD'), [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
        PDO::ATTR_TIMEOUT => 5,
        PDO::MYSQL_ATTR_MULTI_STATEMENTS => false,
    ]);
    // Refuse a privileged account; read-only transaction is a second protection.
    foreach ($pdo->query('SHOW GRANTS')->fetchAll(PDO::FETCH_COLUMN) as $grant) {
        if (!preg_match('/^GRANT (SELECT|USAGE) ON /', $grant) || str_contains($grant, 'WITH GRANT OPTION')) {
            throw new RuntimeException('Read-only account required');
        }
    }
    $pdo->exec('SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ');
    $pdo->exec('START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY');
    $tables = [
        'dim_date' => 'tanggal_key', 'dim_product' => 'product_key',
        'dim_customer' => 'customer_key', 'dim_territory' => 'territory_key',
        'dim_promotion' => 'promotion_key', 'dim_currency' => 'currency_key',
        'dim_ship_method' => 'ship_method_key',
    ];
    $contract = json_decode(file_get_contents(__DIR__ . '/../../olap/source_contract.json'), true, 512, JSON_THROW_ON_ERROR);
    foreach ($contract as $table => $columns) {
        if (!isset($tables[$table]) && $table !== 'fact_online_sales') { throw new RuntimeException('Invalid contract'); }
        foreach ($columns as $column) {
            if (!preg_match('/^[a-z_]+$/D', $column)) { throw new RuntimeException('Invalid contract'); }
        }
        $pdo->query('SELECT `' . implode('`,`', $columns) . "` FROM `$table` LIMIT 0");
    }
    if (isset($_GET['health'])) {
        $pdo->commit();
        respond(200, ['available' => true, 'schema_version' => 1]);
    }
    $dimensions = [];
    $quality = ['missing_references' => [], 'unknown_key_details' => [], 'dimension_rows' => [], 'unknown_member_present' => [], 'duplicate_natural_id_rows' => [], 'duplicate_fact_keys' => 0, 'duplicate_surrogate_keys' => 0];
    $naturalKeys = ['dim_product'=>'product_id','dim_customer'=>'customer_id','dim_territory'=>'territory_id','dim_promotion'=>'special_offer_id','dim_currency'=>'currency_rate_id','dim_ship_method'=>'ship_method_id'];
    foreach ($tables as $table => $key) {
        $dimensions[$table] = [];
        foreach ($pdo->query("SELECT * FROM `$table` ORDER BY `$key`") as $row) {
            foreach ($row as $column => $value) {
                if ($value !== null && (preg_match('/(_key|_id)$/', $column)
                    || in_array($column, ['tahun','semester','kuartal','bulan','minggu_dalam_tahun','tanggal_dalam_bulan','hari_dalam_minggu','is_akhir_pekan','is_current','version','min_qty','max_qty'], true))) {
                    $row[$column] = (int)$value;
                }
            }
            $dimensions[$table][(string)$row[$key]] = $row;
        }
        $quality['dimension_rows'][$table] = count($dimensions[$table]);
        $quality['unknown_member_present'][$table] = isset($dimensions[$table]['-1']);
        $quality['missing_references'][$table] = 0;
        $quality['unknown_key_details'][$table] = 0;
        if (isset($naturalKeys[$table])) {
            $natural = $naturalKeys[$table];
            $quality['duplicate_natural_id_rows'][$table] = (int)$pdo->query("SELECT COUNT(*)-COUNT(DISTINCT `$natural`) FROM `$table`")->fetchColumn();
        }
    }
    $columns = ['sales_detail_key','sales_order_id','tanggal_key','product_key','customer_key','territory_key','promotion_key','currency_key','ship_method_key','order_qty','unit_price','unit_price_discount','line_total'];
    $facts = [];
    $referenced = array_fill_keys(array_keys($tables), []);
    foreach ($pdo->query('SELECT `' . implode('`,`', $columns) . '` FROM fact_online_sales ORDER BY sales_detail_key') as $row) {
        foreach ($tables as $table => $key) {
            $value = (string)$row[$key];
            if (!isset($dimensions[$table][$value])) { throw new RuntimeException('Missing dimension reference'); }
            $referenced[$table][$value] = true;
            if ($value === '-1') { $quality['unknown_key_details'][$table]++; }
        }
        $values = [];
        foreach ($columns as $column) {
            if ($row[$column] === null) { throw new RuntimeException('Required fact value absent'); }
            $values[] = in_array($column, ['unit_price','unit_price_discount','line_total'], true) ? scaled((string)$row[$column]) : (int)$row[$column];
        }
        $facts[] = $values;
    }
    $metrics = $pdo->query('SELECT COUNT(*) AS details, COUNT(DISTINCT f.sales_order_id) AS orders, SUM(f.order_qty) AS units, SUM(f.line_total) AS revenue, COUNT(DISTINCT CASE WHEN c.customer_id <> -1 THEN c.customer_id END) AS active_customers, COUNT(DISTINCT DATE_FORMAT(d.tanggal, "%Y-%m")) AS months, MIN(d.tanggal) AS first_date, MAX(d.tanggal) AS last_date, COUNT(DISTINCT CASE WHEN r.currency_rate_id=-1 THEN f.sales_order_id END) AS orders_without_rate, SUM(f.order_qty*f.unit_price-f.line_total) AS actual_discount, SUM(f.line_total*p.discount_pct) AS estimated_promo_discount FROM fact_online_sales f JOIN dim_customer c ON c.customer_key=f.customer_key JOIN dim_date d ON d.tanggal_key=f.tanggal_key JOIN dim_currency r ON r.currency_key=f.currency_key JOIN dim_promotion p ON p.promotion_key=f.promotion_key')->fetch();
    $metrics['revenue_scaled'] = scaled((string)($metrics['revenue'] ?? '0'));
    $metrics['actual_discount_scaled'] = scaled((string)($metrics['actual_discount'] ?? '0'));
    unset($metrics['revenue'], $metrics['actual_discount']);
    foreach (['details','orders','units','active_customers','months','orders_without_rate'] as $name) { $metrics[$name] = (int)$metrics[$name]; }
    foreach ($tables as $table => $key) {
        $referenced[$table]['-1'] = true;
        $dimensions[$table] = array_intersect_key($dimensions[$table], $referenced[$table]);
    }
    $pdo->commit();
    $factColumns = array_map(fn($column) => in_array($column, ['unit_price','unit_price_discount','line_total'], true) ? $column . '_scaled' : $column, $columns);
    respond(200, [
        'schema_version' => 1,
        'meta' => [
            'source_file' => 'Data Warehouse MySQL lokal', 'source_sha256' => null,
            'source_kind' => 'mysql', 'generated_at' => gmdate('c'),
            'money_scale' => 10000, 'metrics' => $metrics, 'quality' => $quality,
            'currency_label' => 'Nilai sumber (tanpa konversi mata uang)',
        ],
        'dimensions' => $dimensions, 'fact_columns' => $factColumns, 'facts' => $facts,
    ]);
} catch (Throwable $error) {
    if (isset($pdo) && $pdo->inTransaction()) { $pdo->rollBack(); }
    // Never return exception messages, SQL, paths or connection details.
    respond(503, ['available' => false, 'error' => 'Data Warehouse lokal belum tersedia atau konfigurasi belum sesuai. Gunakan snapshot SQL.']);
}
