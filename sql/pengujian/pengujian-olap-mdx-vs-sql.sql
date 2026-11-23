-- =============================================================================
-- PENGUJIAN REKONSILIASI OLAP: MDX VS SQL PEMBANDING
-- Kelompok 2 · Data Warehouse & OLAP · UPN "Veteran" Jawa Timur
-- Berkas: sql/pengujian/pengujian-olap-mdx-vs-sql.sql
-- Database Target: adventureworks_dw
-- Tujuan: Membuktikan bahwa hasil kueri MDX sama persis dengan kueri SQL
-- =============================================================================

USE `adventureworks_dw`;

-- -----------------------------------------------------------------------------
-- 1. PEMBANDING PB-01: Tren Penjualan Tahunan & AOV
-- -----------------------------------------------------------------------------
SELECT 
  d.tahun,
  COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
  SUM(f.order_qty) AS order_quantity,
  ROUND(SUM(f.line_total), 2) AS sales_amount,
  ROUND(SUM(f.line_total) / COUNT(DISTINCT f.sales_order_id), 2) AS average_order_value
FROM fact_online_sales f
JOIN dim_date d ON f.tanggal_key = d.tanggal_key
GROUP BY d.tahun
ORDER BY d.tahun;

-- -----------------------------------------------------------------------------
-- 2. PEMBANDING PB-02: Kategori Produk & Harga Rata-rata per Unit
-- -----------------------------------------------------------------------------
SELECT 
  p.category_name AS kategori,
  ROUND(SUM(f.line_total), 2) AS sales_amount,
  SUM(f.order_qty) AS order_quantity,
  ROUND(SUM(f.line_total) / SUM(f.order_qty), 2) AS average_unit_price
FROM fact_online_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY sales_amount DESC;

-- -----------------------------------------------------------------------------
-- 3. PEMBANDING PB-03: Top 10 Pelanggan VIP & AOV
-- -----------------------------------------------------------------------------
SELECT 
  c.customer_id,
  c.customer_name,
  ROUND(SUM(f.line_total), 2) AS sales_amount,
  COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
  ROUND(SUM(f.line_total) / COUNT(DISTINCT f.sales_order_id), 2) AS average_order_value
FROM fact_online_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.customer_name
ORDER BY sales_amount DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- 4. PEMBANDING PB-04: Penjualan per Grup Wilayah
-- -----------------------------------------------------------------------------
SELECT 
  t.territory_group AS grup_wilayah,
  ROUND(SUM(f.line_total), 2) AS sales_amount,
  COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
  ROUND(SUM(f.line_total) / COUNT(DISTINCT f.sales_order_id), 2) AS average_order_value
FROM fact_online_sales f
JOIN dim_territory t ON f.territory_key = t.territory_key
GROUP BY t.territory_group
ORDER BY sales_amount DESC;

-- -----------------------------------------------------------------------------
-- 5. PEMBANDING PB-05: Penjualan Berdasarkan Program Promosi
-- -----------------------------------------------------------------------------
SELECT 
  p.special_offer_id,
  p.description AS program_promosi,
  p.discount_pct,
  ROUND(SUM(f.line_total), 2) AS sales_amount,
  SUM(f.order_qty) AS order_quantity,
  COUNT(*) AS total_rows
FROM fact_online_sales f
JOIN dim_promotion p ON f.promotion_key = p.promotion_key
GROUP BY p.special_offer_id, p.description, p.discount_pct
ORDER BY sales_amount DESC;

-- -----------------------------------------------------------------------------
-- 6. PEMBANDING PB-06: Kelengkapan Kurs & Distribusi Valuta
-- -----------------------------------------------------------------------------
SELECT 
  CASE WHEN c.currency_rate_id = -1 THEN 'Tanpa Kurs (Default USD)' ELSE 'Dengan Kurs' END AS status_kurs,
  c.to_currency_code AS mata_uang_tujuan,
  COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
  ROUND(SUM(f.line_total), 2) AS sales_amount
FROM fact_online_sales f
JOIN dim_currency c ON f.currency_key = c.currency_key
GROUP BY status_kurs, c.to_currency_code
ORDER BY distinct_orders DESC;

-- -----------------------------------------------------------------------------
-- 7. PEMBANDING PB-07: Sebaran Metode Pengiriman
-- -----------------------------------------------------------------------------
SELECT 
  s.ship_method_id,
  s.ship_method_name,
  ROUND(SUM(f.line_total), 2) AS sales_amount,
  COUNT(DISTINCT f.sales_order_id) AS distinct_orders,
  SUM(f.order_qty) AS order_quantity
FROM fact_online_sales f
JOIN dim_ship_method s ON f.ship_method_key = s.ship_method_key
GROUP BY s.ship_method_id, s.ship_method_name
ORDER BY sales_amount DESC;
