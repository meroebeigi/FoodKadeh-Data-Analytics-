-- SQLite 3.25+; run after scripts/export_analytics.py.
-- Grain: one row per completed order. Never sum order revenue after an item join.
CREATE VIEW IF NOT EXISTS completed_orders AS
SELECT * FROM orders WHERE status = 'Completed';

CREATE VIEW IF NOT EXISTS monthly_kpis AS
WITH monthly AS (
  SELECT strftime('%Y-%m', order_date) AS month,
         COUNT(*) AS completed_orders, SUM(net_revenue) AS revenue,
         COUNT(DISTINCT user_id) AS buying_customers
  FROM completed_orders GROUP BY 1
), previous AS (
  SELECT *, LAG(revenue) OVER (ORDER BY month) AS previous_revenue FROM monthly
)
SELECT *, revenue / completed_orders AS aov,
       (revenue - previous_revenue) / NULLIF(previous_revenue, 0) AS revenue_mom
FROM previous;

-- Session conversion includes orders later cancelled/refunded, as in the notebook.
CREATE VIEW IF NOT EXISTS channel_conversion AS
SELECT traffic_source, device, COUNT(*) AS sessions,
       SUM(converted) AS converted_sessions,
       1.0 * SUM(converted) / NULLIF(COUNT(*), 0) AS conversion_rate
FROM sessions GROUP BY traffic_source, device;

CREATE VIEW IF NOT EXISTS customer_rfm AS
WITH customer AS (
 SELECT user_id, COUNT(*) AS frequency, SUM(net_revenue) AS monetary,
        CAST(julianday('2026-03-01') - julianday(MAX(order_date)) AS INTEGER) AS recency_days
 FROM completed_orders GROUP BY user_id
), scored AS (
 SELECT *, 6 - NTILE(5) OVER (ORDER BY recency_days, user_id) AS r,
        NTILE(5) OVER (ORDER BY frequency, user_id) AS f,
        NTILE(5) OVER (ORDER BY monetary, user_id) AS m
 FROM customer
)
SELECT *, r + f + m AS rfm_score,
 CASE WHEN r >= 4 AND f >= 4 AND m >= 4 THEN 'Champions'
      WHEN r >= 3 AND f >= 3 THEN 'Loyal'
      WHEN r >= 4 AND f <= 2 THEN 'New Customers'
      WHEN r <= 2 AND f >= 3 THEN 'At Risk'
      WHEN r <= 1 THEN 'Lost' ELSE 'Potential Loyalists' END AS segment
FROM scored;

-- First completed-purchase cohorts; future/unobserved months are absent, not zero.
CREATE VIEW IF NOT EXISTS cohort_retention AS
WITH first_purchase AS (
 SELECT user_id, MIN(strftime('%Y-%m', order_date)) AS cohort
 FROM completed_orders GROUP BY user_id
), activity AS (
 SELECT DISTINCT o.user_id, f.cohort,
   (CAST(strftime('%Y', o.order_date) AS INTEGER) - CAST(substr(f.cohort,1,4) AS INTEGER))*12
   + CAST(strftime('%m', o.order_date) AS INTEGER) - CAST(substr(f.cohort,6,2) AS INTEGER) AS month_index
 FROM completed_orders o JOIN first_purchase f USING(user_id)
), sizes AS (
 SELECT cohort, COUNT(*) AS cohort_size FROM first_purchase GROUP BY cohort
), offsets AS (
 SELECT 0 AS month_index UNION ALL SELECT 1 UNION ALL SELECT 2
 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
)
SELECT s.cohort, x.month_index, s.cohort_size, COUNT(a.user_id) AS active_customers,
       1.0 * COUNT(a.user_id) / s.cohort_size AS retention_rate
FROM sizes s CROSS JOIN offsets x
LEFT JOIN activity a ON a.cohort=s.cohort AND a.month_index=x.month_index
WHERE date(s.cohort || '-01', '+' || x.month_index || ' months') <= '2026-02-01'
GROUP BY s.cohort, x.month_index, s.cohort_size;

-- Product sales exclude delivery fees and discounts; not equivalent to net revenue.
CREATE VIEW IF NOT EXISTS category_sales AS
SELECT p.category, SUM(i.quantity) AS units, SUM(i.item_revenue) AS product_sales,
       DENSE_RANK() OVER (ORDER BY SUM(i.item_revenue) DESC) AS sales_rank
FROM order_items i JOIN products p USING(product_id)
JOIN completed_orders o USING(order_id) GROUP BY p.category;
