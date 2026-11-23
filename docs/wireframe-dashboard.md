# Wireframe & Pemetaan Data Dashboard Penjualan Online — AdventureWorks DW

**Kelompok 2 · Data Warehouse & OLAP · Sistem Informasi UPN “Veteran” Jawa Timur**  
**Versi:** 2.2 — Integrasi Fitur Analitis Adaptif (Top Pelanggan VIP PB-03, Top 10 Produk Dinamis PB-02, & Ekspor CSV)  
**Tanggal Pembaruan:** 24 November 2026  
**Acuan Evaluasi:** Prinsip Desain Dosen (Visualisasi Data & Kebutuhan Pekan 14)  
**Status Implementasi Prototipe:** [`dashboard/wireframe-dashboard.html`](../dashboard/wireframe-dashboard.html) (Aktif di `http://localhost:3000/wireframe-dashboard.html`)

---

## 1. Evaluasi Kepatuhan terhadap Prinsip Desain Dosen

Berikut adalah hasil audit dan penyelarasan rancangan dashboard terhadap setiap poin prinsip yang diberikan dosen:

| Prinsip Dosen | Aturan / Standar Evaluasi | Status pada Dashboard | Penyesuaian & Bukti Implementasi |
|---|---|:---:|---|
| **1. Berangkat dari Pertanyaan Bisnis** | Setiap visual wajib menjawab satu pertanyaan bisnis dari piagam proyek. Jika tidak menjawab, hapus. | ✅ **Lolos Penuh** | Setiap visual menjawab 7 Pertanyaan Bisnis resmi (P1 s.d. P7) pada piagam proyek/Bus Matrix `OnlineOrderFlag = 1`. Komponen tidak relevan (seperti Sales Person) ditiadakan karena bernilai NULL di seluruh data online. Menjawab eksplisit **PB-03** (Pelanggan VIP & Berulang). |
| **2. Pemilihan Visual yang Tepat** | Prinsip Visdat: Satu jenis grafik terbaik untuk tiap pertanyaan bisnis. | ✅ **Lolos Penuh** | • **Tren Penjualan (P1):** **Line chart** tren bulanan 38 bulan.<br>• **Kategori & Top Produk (P2):** **Capsule Bar chart** kategori + daftar interaktif Top 10 Produk.<br>• **Pelanggan Berulang & VIP (P3):** **KPI card** frekuensi pesanan + **Modal interaktif Top 10 Pelanggan VIP**.<br>• **Wilayah Tertinggi (P4):** **Bar chart** wilayah & negara.<br>• **Promosi & Diskon (P5):** **Tabel rincian promosi & diskon**.<br>• **Kualitas Data Kurs (P6):** **Quality split bar & tabel valuta**.<br>• **Pengiriman (P7):** **Bar chart** sebaran metode kirim. |
| **3. Urutan Baca (Layout)** | **Atas:** Ringkasan (KPI)<br>**Tengah:** Tren (Line Chart)<br>**Bawah:** Rincian (Bar & Tabel) | ✅ **Lolos Penuh** | Mengikuti alur pandang mata (*Z-pattern / F-pattern*):<br>1. *Atas:* 4 KPI Cards (Nilai Penjualan, Jumlah Pesanan, Pelanggan Aktif, Diskon Promosi).<br>2. *Tengah:* Line Chart tren bulanan 38 bulan.<br>3. *Bawah:* Bar horizontal produk & kategori (P2), Bar wilayah (P4), serta Tabel promosi & diskon (P5). |
| **4. Jumlah Visual per Halaman** | **Maksimal 5 sampai 7 visual per halaman**. Lebih dari itu, pecah menjadi beberapa halaman. | ✅ **Lolos Penuh** | Dashboard dipecah menjadi **2 halaman tematik**:<br>• **Halaman 1 (Penjualan & Produk):** Tepat **5 visual utama** (1 baris KPI + 1 Line Chart + 3 Bar/Tabel Rincian).<br>• **Halaman 2 (Logistik & Kualitas Data):** Tepat **2 visual** (Metode Kirim P7 & Kualitas Kurs P6). |
| **5. Filter Global & Aksi Data** | Filter berlaku untuk semua visual. Dituliskan filter apa saja yang tersedia. | ✅ **Lolos Penuh** | Filter global tertera di header: **Tahun** (`dim_date.tahun`: 2011–2014), **Wilayah** (`dim_territory.territory_group`), dan **Kategori Produk** (`dim_product.category_name`). Dilengkapi tombol **Ekspor CSV** untuk mengunduh snapshot data aktif secara instan. |
| **6. Kesiapan Sumber Data (Pekan 14)** | Backend kecil mengembalikan JSON. Kueri SQL dicatat untuk tiap visual. | ✅ **Lolos Penuh** | Tersedia tab **Spesifikasi Kueri JSON Pekan 14** dan pop-up interaktif pada tiap visual yang merinci endpoint API dan kueri SQL `SELECT` sesuai skema aktual `sql/adventureworks_dw.sql`. |

---

## 2. Pemetaan Data Aktual Hasil Load (`sql/adventureworks_dw.sql`) ke Komponen Wireframe

Seluruh angka pada wireframe telah dipetakan langsung dari data hasil ETL di [`sql/adventureworks_dw.sql`](../sql/adventureworks_dw.sql):

### 2.1 Ringkasan Populasi Tabel Data Warehouse (`adventureworks_dw`)

| Tabel DW | Jumlah Baris Ter-load | Keterangan Pemetaan di Dashboard |
|---|---:|---|
| `fact_online_sales` | **60.398** | 27.659 pesanan unik (`sales_order_id`), 60.398 unit, total `line_total` **$29.358.677,22** |
| `dim_date` | **1.124** | Rentang kalender transaksi online Mei 2011 – Juni 2014 (38 bulan aktif), PK `tanggal_key` |
| `dim_product` | **130** | 130 produk unik terjual online (88 Bikes, 22 Accessories, 20 Clothing), PK `product_key` |
| `dim_customer` | **73.936** | 18.484 pelanggan aktif yang bertransaksi di `fact_online_sales` (29 pelanggan VIP > $10K) |
| `dim_territory` | **40** | 10 wilayah penjualan dalam 3 grup (`North America`, `Pacific`, `Europe`), PK `territory_key` |
| `dim_promotion` | **16** | 4 jenis penawaran aktif di transaksi online (`No Discount`, `Volume Discount 11 to 14`, `Touring-1000`, `Touring-3000`) |
| `dim_currency` | **9.865** | `currency_key = 1` (`currency_rate_id = -1`, Default USD) + kurs `AUD`, `CAD`, `GBP`, `DEM`, `FRF` |
| `dim_ship_method` | **4** | Seluruh pesanan online terhubung ke `XRQ - TRUCK GROUND` (`ship_method_id = 1`) |

---

### 2.2 Pemetaan Angka per Visual & Filter Tahun

| Tahun (`dim_date.tahun`) | Nilai Penjualan (`SUM(line_total)`) | Pesanan Unik (`COUNT(DISTINCT sales_order_id)`) | Pelanggan Aktif (`COUNT(DISTINCT customer_key)`) | Unit Terjual (`SUM(order_qty)`) | Penjualan Promo (`special_offer_id > 1`) | Estimasi Diskon Promo (`line_total * discount_pct`) |
|---|---:|---:|---:|---:|---:|---:|
| **Semua Tahun** | **$29.358.677,22** | **27.659** | **18.484** | **60.398** | **$2.051.070,14** (2.151 baris) | **$48.530,24** |
| **2011** | $3.863.120,21 | 1.201 | 1.201 | 1.201 | $0,00 (0 baris) | $0,00 |
| **2012** | $6.390.599,95 | 2.743 | 2.743 | 2.743 | $463.510,67 (206 baris) | $9.270,21 |
| **2013** | $10.732.127,33 | 12.584 | 10.541 | 28.959 | $1.016.028,10 (1.118 baris) | $27.829,40 |
| **2014** | $8.372.829,73 | 11.131 | 9.898 | 27.495 | $571.531,37 (827 baris) | $11.430,63 |

---

### 2.3 Pemetaan Rincian Visual Bawah & Fitur Analitik Lanjutan

#### A. Kategori & Top 10 Produk Terlaris (`dim_product` - PB-02)
- **Bikes:** **$28.318.144,65 (96,46%)** — 15.205 unit (88 produk)
- **Accessories:** **$700.759,96 (2,39%)** — 36.092 unit (22 produk)
- **Clothing:** **$339.772,61 (1,16%)** — 9.101 unit (20 produk)

| Peringkat | Nama Produk | Kategori | Unit Terjual | Nilai Penjualan ($) | Kontrol Tampilan |
|:---:|---|---|---:|---:|:---:|
| **#1** | Mountain-200 Black, 46 | Bikes | 620 unit | $1.373.469,55 | Default Utama |
| **#2** | Mountain-200 Black, 42 | Bikes | 614 unit | $1.363.142,09 | Default Utama |
| **#3** | Mountain-200 Silver, 38 | Bikes | 596 unit | $1.339.462,79 | Default Utama |
| **#4** | Mountain-200 Silver, 46 | Bikes | 580 unit | $1.301.100,10 | Expandable (Top 4–10) |
| **#5** | Mountain-200 Black, 38 | Bikes | 582 unit | $1.294.866,14 | Expandable (Top 4–10) |
| **#6** | Mountain-200 Silver, 42 | Bikes | 560 unit | $1.257.434,57 | Expandable (Top 4–10) |
| **#7** | Road-150 Red, 48 | Bikes | 337 unit | $1.205.876,99 | Expandable (Top 4–10) |
| **#8** | Road-150 Red, 62 | Bikes | 336 unit | $1.202.298,72 | Expandable (Top 4–10) |
| **#9** | Road-150 Red, 52 | Bikes | 302 unit | $1.080.637,54 | Expandable (Top 4–10) |
| **#10** | Road-150 Red, 56 | Bikes | 295 unit | $1.055.589,65 | Expandable (Top 4–10) |

#### B. Pelanggan Berulang & Top 10 Pelanggan VIP (`dim_customer` - PB-03)
- **Total Pelanggan Aktif:** 18.484 orang.
- **Rata-rata Frekuensi Pembelian:** 1,50 pesanan per pelanggan.
- **Pelanggan VIP (> $10.000 belanja):** 29 orang (dengan rata-rata 5,0 pesanan unik).

| Peringkat | Nama Pelanggan | Customer ID | Frekuensi Pesanan | Total Belanja ($) | Akses di Wireframe |
|:---:|---|:---:|:---:|---:|:---:|
| **#1** | Nichole Nara | 12301 | 5 pesanan | $13.295,38 | Modal Pelanggan VIP |
| **#2** | Kaitlyn J Henderson | 12132 | 5 pesanan | $13.294,27 | Modal Pelanggan VIP |
| **#3** | Margaret He | 12308 | 5 pesanan | $13.269,27 | Modal Pelanggan VIP |
| **#4** | Randall M Dominguez | 12131 | 5 pesanan | $13.265,99 | Modal Pelanggan VIP |
| **#5** | Adriana L Gonzalez | 12300 | 5 pesanan | $13.242,70 | Modal Pelanggan VIP |
| **#6** | Rosa K Hu | 12321 | 5 pesanan | $13.215,65 | Modal Pelanggan VIP |
| **#7** | Brandi D Gill | 12124 | 5 pesanan | $13.195,64 | Modal Pelanggan VIP |
| **#8** | Brad She | 12307 | 5 pesanan | $13.173,19 | Modal Pelanggan VIP |
| **#9** | Francisco A Sara | 12296 | 5 pesanan | $13.164,64 | Modal Pelanggan VIP |
| **#10** | Maurice M Shan | 11433 | 6 pesanan | $12.909,67 | Modal Pelanggan VIP |

#### C. Penjualan per Wilayah (`dim_territory` - PB-04)
- **Grup Wilayah Utama:**
  - **North America (US & Canada):** **$11.367.634,37 (38,72%)** — 12.942 pesanan unik (28.964 unit)
  - **Pacific (Australia):** **$9.061.000,58 (30,86%)** — 6.718 pesanan unik (13.345 unit) — *Negara tunggal dengan omzet tertinggi*
  - **Europe (UK, Germany, France):** **$8.930.042,26 (30,42%)** — 7.999 pesanan unik (18.089 unit)

- **Daftar Lengkap 10 Wilayah Pemasaran (Territory Level):**

| Peringkat | Nama Wilayah | Kode Negara | Grup Wilayah | Pesanan Unik | Unit Terjual | Nilai Penjualan ($) | Pangsa Omzet (%) | Kontrol Tampilan |
|:---:|---|:---:|---|---:|---:|---:|---:|:---:|
| **#1** | Australia | AU | Pacific | 6.718 | 13.345 | $9.061.000,58 | 30,86% | Kartu Bento & Modal |
| **#2** | Southwest | US | North America | 5.473 | 12.265 | $5.718.150,81 | 19,48% | Kartu Bento & Modal |
| **#3** | Northwest | US | North America | 4.058 | 8.993 | $3.649.866,55 | 12,43% | Modal 10 Wilayah |
| **#4** | United Kingdom | GB | Europe | 3.031 | 6.906 | $3.391.712,21 | 11,55% | Modal 10 Wilayah |
| **#5** | Germany | DE | Europe | 2.484 | 5.625 | $2.894.312,34 | 9,86% | Modal 10 Wilayah |
| **#6** | France | FR | Europe | 2.484 | 5.558 | $2.644.017,71 | 9,01% | Modal 10 Wilayah |
| **#7** | Canada | CA | North America | 3.375 | 7.620 | $1.977.844,86 | 6,74% | Modal 10 Wilayah |
| **#8** | Southeast | US | North America | 17 | 39 | $12.238,85 | 0,04% | Modal 10 Wilayah |
| **#9** | Northeast | US | North America | 10 | 27 | $6.532,47 | 0,02% | Modal 10 Wilayah |
| **#10** | Central | US | North America | 9 | 20 | $3.000,83 | 0,01% | Modal 10 Wilayah |
| **TOTAL** | **10 Wilayah** | **-** | **-** | **27.659** | **60.398** | **$29.358.677,22** | **100,00%** | **Data Warehouse** |

#### D. Rincian Promosi & Diskon (`dim_promotion` - PB-05)
- `No Discount` (`0%`): **58.247 baris** (27.119 pesanan) — **$27.307.607,08** (93,01%) — Diskon **$0,00**
- `Volume Discount 11 to 14` (`2%`): **2.118 baris** (2.075 pesanan) — **$2.005.230,23** (6,83%) — Estimasi Diskon **$40.104,60**
- `Touring-1000 Promotion` (`20%`): **13 baris** (13 pesanan) — **$30.992,91** (0,11%) — Estimasi Diskon **$6.198,58**
- `Touring-3000 Promotion` (`15%`): **20 baris** (20 pesanan) — **$14.847,00** (0,05%) — Estimasi Diskon **$2.227,05**

#### E. Kelengkapan Kurs & Distribusi Valuta (`dim_currency` - PB-06)
- **Tanpa Kurs (`currency_rate_id = -1` / Default USD):** **14.860 pesanan (53,73%)** / 33.400 baris detail — **$14.693.465,32**
- **Dengan Kurs (`currency_rate_id > 0`):** **12.799 pesanan (46,27%)** / 26.998 baris detail — **$14.665.211,90**:
  - `AUD`: **6.550 pesanan (23,68%)** — $9.051.988,08
  - `CAD`: **3.147 pesanan (11,38%)** — $1.806.517,44
  - `GBP`: **2.967 pesanan (10,73%)** — $3.388.349,69
  - `DEM`: **76 pesanan (0,27%)** — $237.784,99
  - `FRF`: **59 pesanan (0,21%)** — $180.571,69

#### F. Sebaran Metode Pengiriman (`dim_ship_method` - PB-07)
- **`XRQ - TRUCK GROUND` (`ship_method_id = 1`):** **27.659 pesanan unik (100,0%)** / 60.398 baris detail — **$29.358.677,22**.

---

## 3. Diagram Wireframe Kotak & Label (Sesuai Format Kuliah)

### HALAMAN 1: KINERJA PENJUALAN, PRODUK & WILAYAH

```
+---------------------------------------------------------------------------------------------------------------------+
|  NAVIGASI TAB: [Penjualan & Produk (Aktif)]  [Logistik & Kualitas Data]  [Spesifikasi Kueri JSON]                   |
|  FILTER GLOBAL:                                                                                                     |
|  [Tahun: Semua | 2011 | 2012 | 2013 | 2014]   [Wilayah: Global v]   [Kategori: Semua Kategori v]  [Reset] [Ekspor CSV]|
+---------------------------------------------------------------------------------------------------------------------+
|  RINGKASAN DI ATAS (4 TONAL BLUE BENTO KPI CARDS):                                                                  |
|  +-----------------------+ +-----------------------+ +-----------------------+ +----------------------------------+ |
|  | KPI: Nilai Penjualan  | | KPI: Jumlah Pesanan   | | KPI: Pelanggan Aktif  | | KPI: Penjualan & Diskon Promo    | |
|  | Angka + Delta (P1)    | | Angka + Delta (P1)    | | [10 VIP ->] (P3)      | | Est. Diskon (P5)                 | |
|  | $29.358.677,22        | | 27.659 Pesanan        | | 18.484 Pelanggan      | | $48.530,24                       | |
|  | 60.398 Unit Terjual   | | AOV: $1.061,45        | | 1,50 Pesanan / Cust   | | 2.151 Baris ($2,05M Promo)       | |
|  +-----------------------+ +-----------------------+ +-----------------------+ +----------------------------------+ |
+---------------------------------------------------------------------------------------------------------------------+
|  TREN DI TENGAH:                                                                                                    |
|  +----------------------------------------------------------------------------------------------------------------+ |
|  | Line Chart (P1): Tren Penjualan Bulanan 38 Bulan (Mei 2011 s.d. Juni 2014)                                      | |
|  | - Sumbu X: Bulan & Tahun (dim_date)                                                                            | |
|  | - Garis Solid: Nilai Penjualan ($) | Garis Putus-putus: Kuantitas Unit Terjual                                 | |
|  | - Titik Puncak: Mei 2014 ($1.951.195,90 • 5.624 Unit • 2.232 Pesanan)                                          | |
|  | [Tombol: Lihat Kueri SQL P1]                                                                                   | |
|  +----------------------------------------------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------------------------------------------+
|  RINCIAN DI BAWAH (3 KOLOM ANALITIK):                                                                               |
|  +-----------------------------+ +-----------------------------+ +------------------------------------------------+ |
|  | Bar Chart & Top 10 (P2)     | | Bar Chart Wilayah (P4)      | | Tabel Promosi & Diskon (P5)                    | |
|  | Kategori & Produk Terlaris  | | Penjualan per Wilayah       | | Rincian Diskon Penjualan                       | |
|  | - Capsule Bar Kategori:     | | - North America: $11,37M    | | - No Discount: 58.247 baris ($27,31M)          | |
|  |   * Bikes: 96,46% ($28,32M) | | - Pacific (Aus): $9,06M     | | - Volume Disc 11-14: 2.118 baris ($2,01M)      | |
|  |   * Accessories: 2,39%      | | - Europe: $8,93M            | | - Touring Promo: 33 baris ($45,8K)             | |
|  |   * Clothing: 1,16%         | | Sumbu: SUM(line_total)      | | Total Estimasi Diskon: $48.530,24              | |
|  | - Top 3 Produk (Default)    | | - [Semua 10 Wilayah ->]     | | Total Estimasi Diskon: $48.530,24              | |
|  | - [Tampilkan Top 4-10 Produk]                               | |                                                | |
|  | [Tombol: Lihat Kueri SQL P2]| | [Tombol: Lihat Kueri SQL P4]| | [Tombol: Lihat Kueri SQL P5]                   | |
|  +-----------------------------+ +-----------------------------+ +------------------------------------------------+ |
+---------------------------------------------------------------------------------------------------------------------+
|  POP-UP MODAL (TERSEMBUNYI, AKTIF SAAT DIKLIK):                                                                     |
|  • Modal Kueri SQL: Menampilkan kueri SQL acuan dan penjelasan visual per pertanyaan bisnis (P1–P7)                 |
|  • Modal Top 10 Pelanggan VIP (PB-03): Menampilkan tabel nama, customer_id, frekuensi pesanan & total belanja       |
|  • Modal 10 Wilayah Pemasaran (PB-04): Menampilkan tabel lengkap 10 wilayah (omzet, pesanan, unit, pangsa pasar)   |
+---------------------------------------------------------------------------------------------------------------------+
```

### HALAMAN 2: LOGISTIK PENGIRIMAN & KUALITAS DATA MATA UANG

```
+---------------------------------------------------------------------------------------------------------------------+
|  NAVIGASI TAB: [Penjualan & Produk]  [Logistik & Kualitas Data (Aktif)]  [Spesifikasi Kueri JSON]                   |
|  FILTER GLOBAL:                                                                                                     |
|  [Tahun: Semua | 2011 | 2012 | 2013 | 2014]   [Wilayah: Global v]   [Kategori: Semua Kategori v]  [Reset] [Ekspor CSV]|
+---------------------------------------------------------------------------------------------------------------------+
|  RINCIAN OPERASIONAL & AUDIT DATA WAREHOUSE:                                                                        |
|  +---------------------------------------------------+ +----------------------------------------------------------+ |
|  | Bar Chart (P7)                                    | | Quality Split & Tabel Valuta (P6)                        | |
|  | Sebaran Metode Pengiriman                         | | Kelengkapan Kurs & Distribusi Valuta                     | |
|  |                                                   | |                                                          | |
|  | - 🚚 XRQ - TRUCK GROUND (ship_method_id = 1):     | | - Bar Proporsi Referensi Kurs:                           | |
|  |   27.659 pesanan unik (100,0%) / 60.398 detail    | |   * Tanpa Kurs (-1 / USD): 14.860 pesanan (53,73%)       | |
|  | - Metode Lain di Katalog OLTP:                    | |   * Dengan Kurs: 12.799 pesanan (46,27%)                 | |
|  |   0 pesanan online (0,0%)                         | | - Tabel Sebaran Valuta Transaksi:                        | |
|  |                                                   | |   USD (14.860), AUD (6.550), CAD (3.147),                | |
|  | Ukuran: COUNT(DISTINCT sales_order_id)            | |   GBP (2.967), DEM (76), FRF (59)                        | |
|  | [Tombol: Lihat Kueri SQL P7]                      | | [Tombol: Lihat Kueri SQL P6]                             | |
|  +---------------------------------------------------+ +----------------------------------------------------------+ |
+---------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Spesifikasi Kueri Backend JSON Sesuai Skema `sql/adventureworks_dw.sql` (Pekan 14)

### Visual 1 — KPI Ringkasan: `GET /api/kpi/summary`
```sql
SELECT 
    ROUND(SUM(f.line_total), 2) AS total_sales,
    COUNT(DISTINCT f.sales_order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS active_customers,
    SUM(f.order_qty) AS total_units,
    ROUND(SUM(f.line_total) / COUNT(DISTINCT f.sales_order_id), 2) AS aov,
    ROUND(SUM(CASE WHEN p.special_offer_id > 1 THEN f.line_total ELSE 0 END), 2) AS promo_sales,
    ROUND(SUM(f.line_total * p.discount_pct), 2) AS estimated_promo_discount
FROM fact_online_sales f
JOIN dim_promotion p ON f.promotion_key = p.promotion_key;
```

### Visual 2 — Line Chart Tren Bulanan (PB-01): `GET /api/trends/monthly`
```sql
SELECT 
    d.tahun,
    d.bulan,
    d.nama_bulan,
    COUNT(DISTINCT f.sales_order_id) AS monthly_orders,
    SUM(f.order_qty) AS monthly_units,
    ROUND(SUM(f.line_total), 2) AS monthly_sales
FROM fact_online_sales f
JOIN dim_date d ON f.tanggal_key = d.tanggal_key
GROUP BY d.tahun, d.bulan, d.nama_bulan
ORDER BY d.tahun, d.bulan;
```

### Visual 3 — Bar Chart Kategori & Top 10 Produk (PB-02): `GET /api/products/ranking`
```sql
SELECT 
    p.category_name,
    p.product_name,
    SUM(f.order_qty) AS units_sold,
    ROUND(SUM(f.line_total), 2) AS sales_amount
FROM fact_online_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_key, p.category_name, p.product_name
ORDER BY sales_amount DESC
LIMIT 10;
```

### Visual 4 — Modal Top 10 Pelanggan VIP (PB-03): `GET /api/customers/top-vip`
```sql
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', COALESCE(c.middle_name, ''), ' ', c.last_name) AS customer_name,
    COUNT(DISTINCT f.sales_order_id) AS total_orders,
    ROUND(SUM(f.line_total), 2) AS total_spent
FROM fact_online_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.first_name, c.middle_name, c.last_name
HAVING total_spent > 10000
ORDER BY total_spent DESC
LIMIT 10;
```

### Visual 5 — Bar Chart Penjualan per Wilayah (PB-04): `GET /api/regions/sales`
```sql
SELECT 
    t.territory_group,
    t.country_code,
    t.territory_name,
    COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
    ROUND(SUM(f.line_total), 2) AS sales_amount
FROM fact_online_sales f
JOIN dim_territory t ON f.territory_key = t.territory_key
GROUP BY t.territory_group, t.country_code, t.territory_name
ORDER BY sales_amount DESC;
```

### Visual 6 — Tabel Promosi & Diskon (PB-05): `GET /api/promotions/details`
```sql
SELECT 
    p.special_offer_id,
    p.description AS jenis_penawaran,
    p.discount_pct,
    COUNT(*) AS jumlah_baris,
    COUNT(DISTINCT f.sales_order_id) AS jumlah_pesanan,
    ROUND(SUM(f.line_total), 2) AS nilai_penjualan,
    ROUND(SUM(f.line_total * p.discount_pct), 2) AS estimasi_diskon
FROM fact_online_sales f
JOIN dim_promotion p ON f.promotion_key = p.promotion_key
GROUP BY p.promotion_key, p.special_offer_id, p.description, p.discount_pct
ORDER BY nilai_penjualan DESC;
```

### Visual 7 — Quality Split Mata Uang & Kurs (PB-06): `GET /api/currency/quality`
```sql
SELECT 
    CASE WHEN c.currency_rate_id = -1 THEN 'Tanpa Kurs (Default USD)' ELSE 'Dengan Kurs' END AS status_kurs,
    c.to_currency_code,
    COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
    COUNT(*) AS detail_rows,
    ROUND(SUM(f.line_total), 2) AS total_sales
FROM fact_online_sales f
JOIN dim_currency c ON f.currency_key = c.currency_key
GROUP BY status_kurs, c.to_currency_code
ORDER BY distinct_orders DESC;
```

### Visual 8 — Bar Chart Metode Pengiriman (PB-07): `GET /api/shipping/distribution`
```sql
SELECT 
    s.ship_method_id,
    s.ship_method_name,
    COUNT(DISTINCT f.sales_order_id) AS total_orders,
    COUNT(*) AS detail_rows,
    ROUND(SUM(f.line_total), 2) AS sales_amount
FROM fact_online_sales f
JOIN dim_ship_method s ON f.ship_method_key = s.ship_method_key
GROUP BY s.ship_method_id, s.ship_method_name
ORDER BY total_orders DESC;
```
