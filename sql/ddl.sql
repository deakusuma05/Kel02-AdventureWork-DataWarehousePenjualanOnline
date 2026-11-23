-- =============================================================================
-- Kelompok 2: inisialisasi non-destruktif Data Warehouse Penjualan Online.
-- Pilih database target secara eksplisit pada koneksi sebelum menjalankan skrip.
-- CREATE IF NOT EXISTS + INSERT anggota Unknown yang belum ada mempertahankan data.
-- Ini bukan migrasi struktur tabel lama: bandingkan INFORMATION_SCHEMA sebelum ETL.
-- Struktur mengikuti ETL aktif (termasuk periode biaya produk Pekan 13).
-- Rebuild terisolasi dipisahkan ke ddl_rebuild.sql; jangan memakai dump untuk rerun.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 2. CREATE DIMENSION TABLES
-- -----------------------------------------------------------------------------

-- 2.1 Dimensi kalender internal; kesesuaian standar dosen perlu dokumen resmi
CREATE TABLE IF NOT EXISTS `dim_date` (
  `tanggal_key` int(11) NOT NULL,
  `tanggal` date NOT NULL,
  `tahun` int(11) NOT NULL,
  `semester` int(11) NOT NULL,
  `kuartal` int(11) NOT NULL,
  `bulan` int(11) NOT NULL,
  `nama_bulan` varchar(20) NOT NULL,
  `minggu_dalam_tahun` int(11) NOT NULL,
  `tanggal_dalam_bulan` int(11) NOT NULL,
  `hari_dalam_minggu` int(11) NOT NULL,
  `nama_hari` varchar(20) NOT NULL,
  `is_akhir_pekan` tinyint(1) NOT NULL,
  PRIMARY KEY (`tanggal_key`),
  UNIQUE KEY `uq_dim_date_tanggal` (`tanggal`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.2 Dimensi Produk (dim_product)
CREATE TABLE IF NOT EXISTS `dim_product` (
  `product_key` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `product_name` varchar(100) DEFAULT NULL,
  `product_number` varchar(50) DEFAULT NULL,
  `subcategory_name` varchar(100) DEFAULT NULL,
  `category_name` varchar(100) DEFAULT NULL,
  `standard_cost` decimal(19,4) NOT NULL DEFAULT 0.0000,
  `berlaku_mulai` date NOT NULL DEFAULT '1900-01-01',
  `berlaku_sampai` date NOT NULL DEFAULT '9999-12-31',
  PRIMARY KEY (`product_key`),
  KEY `idx_product_period` (`product_id`, `berlaku_mulai`, `berlaku_sampai`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.3 Dimensi Pelanggan (dim_customer)
CREATE TABLE IF NOT EXISTS `dim_customer` (
  `customer_key` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) NOT NULL,
  `account_number` varchar(30) DEFAULT NULL,
  `customer_type` varchar(20) DEFAULT NULL,
  `customer_name` varchar(150) DEFAULT NULL,
  `territory_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`customer_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.4 Dimensi Wilayah (dim_territory)
CREATE TABLE IF NOT EXISTS `dim_territory` (
  `territory_key` int(11) NOT NULL AUTO_INCREMENT,
  `territory_id` int(11) NOT NULL,
  `territory_name` varchar(50) DEFAULT NULL,
  `country_code` varchar(3) DEFAULT NULL,
  `territory_group` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`territory_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.5 Dimensi Promosi (dim_promotion)
CREATE TABLE IF NOT EXISTS `dim_promotion` (
  `promotion_key` int(11) NOT NULL AUTO_INCREMENT,
  `special_offer_id` int(11) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `discount_pct` decimal(10,4) DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`promotion_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.6 Dimensi Mata Uang & Kurs (dim_currency)
CREATE TABLE IF NOT EXISTS `dim_currency` (
  `currency_key` int(11) NOT NULL AUTO_INCREMENT,
  `currency_rate_id` int(11) NOT NULL,
  `from_currency_code` varchar(3) DEFAULT NULL,
  `to_currency_code` varchar(3) DEFAULT NULL,
  `average_rate` decimal(19,4) DEFAULT NULL,
  `end_of_day_rate` decimal(19,4) DEFAULT NULL,
  PRIMARY KEY (`currency_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2.7 Dimensi Metode Pengiriman (dim_ship_method)
CREATE TABLE IF NOT EXISTS `dim_ship_method` (
  `ship_method_key` int(11) NOT NULL AUTO_INCREMENT,
  `ship_method_id` int(11) NOT NULL,
  `ship_method_name` varchar(50) DEFAULT NULL,
  `ship_base` decimal(19,4) DEFAULT NULL,
  `ship_rate` decimal(19,4) DEFAULT NULL,
  PRIMARY KEY (`ship_method_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. CREATE FACT TABLE
-- -----------------------------------------------------------------------------

-- 3.1 Tabel Fakta Penjualan Online (fact_online_sales)
CREATE TABLE IF NOT EXISTS `fact_online_sales` (
  `sales_detail_key` int(11) NOT NULL,
  `sales_order_id` int(11) NOT NULL,
  `tanggal_key` int(11) NOT NULL,
  `product_key` int(11) NOT NULL,
  `customer_key` int(11) NOT NULL,
  `territory_key` int(11) NOT NULL,
  `promotion_key` int(11) NOT NULL,
  `currency_key` int(11) NOT NULL,
  `ship_method_key` int(11) NOT NULL,
  `order_qty` int(11) NOT NULL,
  `unit_price` decimal(19,4) NOT NULL,
  `unit_price_discount` decimal(19,4) NOT NULL,
  `line_total` decimal(19,4) NOT NULL,
  PRIMARY KEY (`sales_detail_key`),
  
  -- Indeks untuk optimasi query analitik OLAP
  KEY `idx_sales_order_id` (`sales_order_id`),
  KEY `idx_fk_tanggal` (`tanggal_key`),
  KEY `idx_fk_product` (`product_key`),
  KEY `idx_fk_customer` (`customer_key`),
  KEY `idx_fk_territory` (`territory_key`),
  KEY `idx_fk_promotion` (`promotion_key`),
  KEY `idx_fk_currency` (`currency_key`),
  KEY `idx_fk_ship_method` (`ship_method_key`),
  
  -- Foreign Key Constraints (Integritas Referensial ke 7 Dimensi)
  CONSTRAINT `fk_fact_tanggal` FOREIGN KEY (`tanggal_key`) REFERENCES `dim_date` (`tanggal_key`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_fact_product` FOREIGN KEY (`product_key`) REFERENCES `dim_product` (`product_key`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_fact_customer` FOREIGN KEY (`customer_key`) REFERENCES `dim_customer` (`customer_key`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_fact_territory` FOREIGN KEY (`territory_key`) REFERENCES `dim_territory` (`territory_key`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_fact_promotion` FOREIGN KEY (`promotion_key`) REFERENCES `dim_promotion` (`promotion_key`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_fact_currency` FOREIGN KEY (`currency_key`) REFERENCES `dim_currency` (`currency_key`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_fact_ship_method` FOREIGN KEY (`ship_method_key`) REFERENCES `dim_ship_method` (`ship_method_key`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. INJEKSI BARIS DEFAULT / UNKNOWN (-1) PADA SELURUH DIMENSI
-- -----------------------------------------------------------------------------

-- Baris -1 untuk dim_date
INSERT INTO `dim_date` (
  `tanggal_key`, `tanggal`, `tahun`, `semester`, `kuartal`, `bulan`, 
  `nama_bulan`, `minggu_dalam_tahun`, `tanggal_dalam_bulan`, `hari_dalam_minggu`, 
  `nama_hari`, `is_akhir_pekan`
)
SELECT -1, '1900-01-01', 1900, 1, 1, 1, 
  'Unknown', 1, 1, 1, 
  'Unknown', 0
WHERE NOT EXISTS (SELECT 1 FROM `dim_date` WHERE `tanggal_key` = -1);

-- Baris -1 untuk dim_product
INSERT INTO `dim_product` (
  `product_key`, `product_id`, `product_name`, `product_number`, 
  `subcategory_name`, `category_name`
)
SELECT -1, -1, 'Unknown Product', 'UNKNOWN', 
  'Unknown Subcategory', 'Unknown Category'
WHERE NOT EXISTS (SELECT 1 FROM `dim_product` WHERE `product_key` = -1);

-- Baris -1 untuk dim_customer
INSERT INTO `dim_customer` (
  `customer_key`, `customer_id`, `account_number`, `customer_type`, 
  `customer_name`, `territory_id`
)
SELECT -1, -1, 'UNKNOWN', 'Unknown', 
  'Unknown Customer', -1
WHERE NOT EXISTS (SELECT 1 FROM `dim_customer` WHERE `customer_key` = -1);

-- Baris -1 untuk dim_territory
INSERT INTO `dim_territory` (
  `territory_key`, `territory_id`, `territory_name`, `country_code`, 
  `territory_group`
)
SELECT -1, -1, 'Unknown Territory', 'UNK', 
  'Unknown Group'
WHERE NOT EXISTS (SELECT 1 FROM `dim_territory` WHERE `territory_key` = -1);

-- Baris -1 untuk dim_promotion
INSERT INTO `dim_promotion` (
  `promotion_key`, `special_offer_id`, `description`, `discount_pct`, 
  `type`, `category`
)
SELECT -1, -1, 'Unknown Promotion', 0.0000, 
  'Unknown', 'Unknown'
WHERE NOT EXISTS (SELECT 1 FROM `dim_promotion` WHERE `promotion_key` = -1);

-- Baris -1 untuk dim_currency
INSERT INTO `dim_currency` (
  `currency_key`, `currency_rate_id`, `from_currency_code`, `to_currency_code`, 
  `average_rate`, `end_of_day_rate`
)
SELECT -1, -1, NULL, NULL, 
  NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `dim_currency` WHERE `currency_key` = -1);

-- Baris -1 untuk dim_ship_method
INSERT INTO `dim_ship_method` (
  `ship_method_key`, `ship_method_id`, `ship_method_name`, `ship_base`, 
  `ship_rate`
)
SELECT -1, -1, 'Unknown Ship Method', 0.0000, 
  0.0000
WHERE NOT EXISTS (SELECT 1 FROM `dim_ship_method` WHERE `ship_method_key` = -1);

-- =============================================================================
-- SELESAI. Eksekusi ulang tidak menghapus/mengubah baris yang sudah ada.
-- =============================================================================
