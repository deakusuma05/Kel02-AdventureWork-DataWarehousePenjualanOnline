-- Jalankan pada skema DW terpilih; hanya membuat view. Akun runtime cukup SELECT.
CREATE OR REPLACE SQL SECURITY INVOKER VIEW adventureworks_dw.v_dim_currency_cube AS
SELECT currency_key, currency_rate_id, from_currency_code,
       CASE WHEN currency_rate_id = -1 THEN 'Tanpa referensi kurs' ELSE to_currency_code END AS to_currency_code,
       average_rate, end_of_day_rate,
       CASE WHEN currency_rate_id = -1 THEN 'Tanpa referensi kurs' ELSE 'Memiliki referensi kurs' END AS rate_status
FROM adventureworks_dw.dim_currency;

CREATE OR REPLACE SQL SECURITY INVOKER VIEW adventureworks_dw.v_online_sales_cube AS
SELECT f.*,
       CASE WHEN c.customer_id = -1 THEN NULL ELSE c.customer_id END AS customer_business_id,
       f.line_total * p.discount_pct AS estimated_promo_discount_value,
       CASE WHEN r.currency_rate_id = -1 THEN f.sales_order_id ELSE NULL END AS orders_without_currencyrate_key
FROM adventureworks_dw.fact_online_sales f
JOIN adventureworks_dw.dim_customer c ON c.customer_key = f.customer_key
JOIN adventureworks_dw.dim_promotion p ON p.promotion_key = f.promotion_key
JOIN adventureworks_dw.dim_currency r ON r.currency_key = f.currency_key;
