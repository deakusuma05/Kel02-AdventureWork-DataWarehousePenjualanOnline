-- Semua difference harus 0 pada database yang sama, setelah preflight.
SELECT 'details' AS metric,
 (SELECT COUNT(*) FROM adventureworks_dw.fact_online_sales) -
 (SELECT COUNT(*) FROM adventureworks_dw.v_online_sales_cube) AS difference
UNION ALL SELECT 'orders',
 (SELECT COUNT(DISTINCT sales_order_id) FROM adventureworks_dw.fact_online_sales) -
 (SELECT COUNT(DISTINCT sales_order_id) FROM adventureworks_dw.v_online_sales_cube)
UNION ALL SELECT 'revenue',
 (SELECT SUM(line_total) FROM adventureworks_dw.fact_online_sales) -
 (SELECT SUM(line_total) FROM adventureworks_dw.v_online_sales_cube)
UNION ALL SELECT 'units',
 (SELECT SUM(order_qty) FROM adventureworks_dw.fact_online_sales) -
 (SELECT SUM(order_qty) FROM adventureworks_dw.v_online_sales_cube);

SELECT COUNT(*) AS details, COUNT(DISTINCT sales_order_id) AS orders,
 COUNT(DISTINCT customer_business_id) AS active_customers,
 SUM(line_total) AS revenue, SUM(order_qty) AS units,
 SUM(estimated_promo_discount_value) AS estimated_promo_discount,
 COUNT(DISTINCT orders_without_currencyrate_key) AS orders_without_rate
FROM adventureworks_dw.v_online_sales_cube;
