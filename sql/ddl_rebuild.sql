-- REBUILD DESTRUKTIF: hanya untuk database sementara berawalan audit_ atau test_.
-- Backup dan validasi pemulihan dahulu. Tidak boleh dipakai pada database utama.
-- Pilih database, kemudian SET @confirm_dw_rebuild = DATABASE(); pada sesi yang sama.
-- Seluruh DROP berada DI DALAM guard; --force tidak dapat melewati SIGNAL.
-- Setelah berhasil, jalankan ddl.sql untuk membangun skema kosong.
DELIMITER $$
DROP PROCEDURE IF EXISTS rebuild_dw_isolated$$
CREATE PROCEDURE rebuild_dw_isolated()
BEGIN
  IF DATABASE() IS NULL OR DATABASE() NOT REGEXP '^(audit_|test_)'
     OR @confirm_dw_rebuild IS NULL OR @confirm_dw_rebuild <> DATABASE() THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rebuild ditolak: perlu database audit_/test_ dan konfirmasi nama database pada sesi ini';
  ELSE
    DROP TABLE IF EXISTS fact_online_sales;
    DROP TABLE IF EXISTS dim_ship_method;
    DROP TABLE IF EXISTS dim_currency;
    DROP TABLE IF EXISTS dim_promotion;
    DROP TABLE IF EXISTS dim_territory;
    DROP TABLE IF EXISTS dim_customer;
    DROP TABLE IF EXISTS dim_product;
    DROP TABLE IF EXISTS dim_date;
  END IF;
END$$
CALL rebuild_dw_isolated()$$
DROP PROCEDURE rebuild_dw_isolated$$
DELIMITER ;
