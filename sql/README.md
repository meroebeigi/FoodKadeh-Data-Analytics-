# SQL analytics

Executable SQLite analysis of the notebook's synthetic food-commerce data. Demonstrates CTEs, joins, conditional segmentation, window functions (`LAG`, `NTILE`, `DENSE_RANK`), cohort analysis, and aggregation at the correct grain.

From the repository root:

```bash
pip install numpy pandas matplotlib scikit-learn
python scripts/export_analytics.py
sqlite3 data/foodkadeh.db "SELECT * FROM monthly_kpis;"
```

The exporter runs the first notebook generator once with seed 42, builds five source tables, installs [analytics views](01_analytics.sql), exports CSVs, and checks revenue/order reconciliation, cohort Month 0, and order-to-user integrity. The notebook contains a repeated generator, so its later outputs and the historical README totals may differ from this canonical run. The executable output is authoritative for these additions.

`orders` has one row per order; `order_items` has one row per order/product; `sessions` has one row per session. Customer and product IDs identify dimension rows. Revenue means completed-order net revenue, including delivery and subtracting discounts. Category sales use item revenue only. Neither metric is platform commission or profit.

Conversion = converted sessions / all retained sessions, including conversions later cancelled or refunded. Repeat purchase rate = buyers with at least two completed orders / all completed-order buyers. RFM uses a fixed snapshot of 2026-03-01 and completed purchases only; never-buyers are excluded. `NTILE` tie-breaking is deterministic by user ID but can differ from Pandas `qcut`. Cohorts use first completed purchase; observed inactive months are zero, future months absent. This is a historical six-month demonstration; extend the date grid and snapshot before using another period.
