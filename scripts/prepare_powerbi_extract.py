"""Run after export_analytics.py; reproduce the static extract embedded in FoodKadeh.pbix."""
import sqlite3
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1] / 'data'
with sqlite3.connect(root / 'foodkadeh.db') as db:
    df = pd.read_sql_query('''WITH sales AS (
      SELECT strftime('%Y-%m',o.order_date) AS Month,u.city AS City,
       SUM(o.net_revenue) AS NetRevenue,
       SUM(CASE WHEN o.status='Completed' THEN 1 ELSE 0 END) AS CompletedOrders,
       SUM(CASE WHEN o.status='Completed' THEN o.delivery_time_min ELSE 0 END) AS DeliveryMinutes
      FROM orders o JOIN users u USING(user_id) GROUP BY 1,2
    ), traffic AS (
      SELECT strftime('%Y-%m',s.session_date) AS Month,u.city AS City,
       COUNT(*) AS Sessions,SUM(s.converted) AS ConvertedSessions
      FROM sessions s JOIN users u USING(user_id) GROUP BY 1,2
    ) SELECT t.Month,t.City,ROUND(COALESCE(s.NetRevenue,0),2) AS NetRevenue,
       COALESCE(s.CompletedOrders,0) AS CompletedOrders,ROUND(COALESCE(s.DeliveryMinutes,0),1) AS DeliveryMinutes,
       t.Sessions,t.ConvertedSessions
      FROM traffic t LEFT JOIN sales s USING(Month,City) ORDER BY 1,2''', db)
    expected = db.execute('SELECT SUM(net_revenue), COUNT(*) FROM completed_orders').fetchone()
    assert round(df.NetRevenue.sum(), 2) == round(expected[0], 2)
    assert df.CompletedOrders.sum() == expected[1]
    assert df.Sessions.sum() == db.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
    assert len(df) == 30 and not df.duplicated(['Month', 'City']).any()
    df.to_csv(root / 'PowerBI_MonthlyCity.csv', index=False)
    df.to_csv(root / 'PowerBI_MonthlyCity.tsv', index=False, sep='\t')
    print(f'Saved {len(df)} rows; revenue {df.NetRevenue.sum():,.2f}; orders {df.CompletedOrders.sum():,}')
