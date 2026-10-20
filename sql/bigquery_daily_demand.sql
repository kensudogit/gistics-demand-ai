-- BigQuery Standard SQL. Replace project/dataset. Not executed in the local demo.
-- raw.orders: order_id, sku_id, site_id, ordered_at(TIMESTAMP), quantity(INT64), status
SELECT
  DATE(ordered_at, 'Asia/Tokyo') AS demand_date,
  site_id,
  sku_id,
  SUM(quantity) AS demand_units
FROM `your-project.raw.orders`
WHERE status = 'completed'
  AND ordered_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY 1, 2, 3;
