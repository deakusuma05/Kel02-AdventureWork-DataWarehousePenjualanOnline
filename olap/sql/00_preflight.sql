-- Daftar kolom wajib diperiksa melalui source_contract.json dan validator.
-- Query berikut harus mengembalikan missing_reference = 0.
SELECT COUNT(*) AS missing_reference
FROM adventureworks_dw.fact_online_sales f
LEFT JOIN adventureworks_dw.dim_tanggal d ON d.tanggal_key=f.tanggal_key
LEFT JOIN adventureworks_dw.dim_product p ON p.product_key=f.product_key
LEFT JOIN adventureworks_dw.dim_customer c ON c.customer_key=f.customer_key
LEFT JOIN adventureworks_dw.dim_territory t ON t.territory_key=f.territory_key
LEFT JOIN adventureworks_dw.dim_promotion pr ON pr.promotion_key=f.promotion_key
LEFT JOIN adventureworks_dw.dim_currency r ON r.currency_key=f.currency_key
LEFT JOIN adventureworks_dw.dim_ship_method s ON s.ship_method_key=f.ship_method_key
WHERE d.tanggal_key IS NULL OR p.product_key IS NULL OR c.customer_key IS NULL
 OR t.territory_key IS NULL OR pr.promotion_key IS NULL OR r.currency_key IS NULL OR s.ship_method_key IS NULL;
SELECT sales_detail_key,COUNT(*) AS duplicate_count FROM adventureworks_dw.fact_online_sales
GROUP BY sales_detail_key HAVING COUNT(*)>1;
