# SQL analytics

Executable SQLite analysis of the notebook's synthetic food-commerce data. Demonstrates CTEs, joins, conditional segmentation, window functions (`LAG`, `NTILE`, `DENSE_RANK`), cohort analysis, and aggregation at the correct grain.

From the repository root:

```bash
pip install numpy pandas matplotlib scikit-learn
python scripts/export_analytics.py
sqlite3 data/foodkadeh.db "SELECT * FROM monthly_kpis;"
```

The exporter and notebook both import `scripts/foodkadeh_data.py` with seed 42. The exporter builds five source tables, recreates the analytical views, exports CSVs, and validates revenue, orders, cohorts and referential integrity. Run `python scripts/validate_consistency.py` after preparing both Power BI extracts for cross-layer checks.

`orders` has one row per order; `order_items` has one row per order/product; `sessions` has one row per session. Customer and product IDs identify dimension rows. Revenue means completed-order net revenue, including delivery and subtracting discounts. Category sales use item revenue only. Neither metric is platform commission or profit.

Conversion = converted sessions / all retained sessions, including conversions later cancelled or refunded. 45-day inactivity is recency >45 days at the snapshot, not the complement of repeat buying. Repeat purchase rate = buyers with at least two completed orders / all completed-order buyers. RFM uses a fixed snapshot of 2026-03-01 and completed purchases only; never-buyers are excluded. `NTILE` tie-breaking is deterministic by user ID; the notebook now evaluates this same SQL view rather than a separate `qcut` implementation. Cohorts use first completed purchase; observed inactive months are zero, future months absent. This is a historical six-month demonstration; extend the date grid and snapshot before using another period.
