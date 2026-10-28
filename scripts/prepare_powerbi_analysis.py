"""Reproduce the four SQL snapshots embedded as calculated tables in the report."""
import sqlite3
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1] / "data"
queries = {
    "Acquisition": """SELECT traffic_source AS Channel, device AS Device,
        sessions AS Sessions, converted_sessions AS Conversions
        FROM channel_conversion ORDER BY traffic_source, device""",
    "Retention": """SELECT cohort AS Cohort, month_index AS MonthIndex,
        cohort_size AS CohortSize, active_customers AS ActiveBuyers
        FROM cohort_retention ORDER BY cohort, month_index""",
    "CustomerSegments": """SELECT segment AS Segment, COUNT(*) AS Customers,
        ROUND(SUM(monetary),2) AS Revenue, SUM(frequency) AS Orders,
        SUM(recency_days > 45) AS Inactive45, SUM(frequency > 1) AS RepeatBuyers
        FROM customer_rfm GROUP BY segment ORDER BY segment""",
    "CategorySales": """SELECT category AS Category, units AS Units,
        ROUND(product_sales,2) AS Sales FROM category_sales ORDER BY sales_rank""",
}
with sqlite3.connect(root / "foodkadeh.db") as db:
    frames = {name: pd.read_sql_query(query, db) for name, query in queries.items()}
    assert frames["Acquisition"].Sessions.sum() == 9838
    assert frames["Acquisition"].Conversions.sum() == 1698
    customers = frames["CustomerSegments"]
    assert customers.Customers.sum() == 1047
    assert customers.RepeatBuyers.sum() == 335
    assert customers.Inactive45.sum() == 442
    assert round(customers.Revenue.sum(), 2) == 72431.22
    retention = frames["Retention"]
    zero = retention.loc[retention.MonthIndex == 0]
    assert (zero.ActiveBuyers == zero.CohortSize).all()
    assert not retention.duplicated(["Cohort", "MonthIndex"]).any()
    assert frames["CategorySales"].Units.sum() == 3899
    for name, frame in frames.items():
        frame.to_csv(root / f"PowerBI_{name}.csv", index=False)
        print(f"{name}: {len(frame)} validated rows")
