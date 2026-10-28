"""Export one canonical notebook generation run into SQLite and Power BI CSVs."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
nb = json.loads((ROOT / 'FoodKadeh.ipynb').read_text(encoding='utf-8'))
code = '\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code')
# The notebook repeats its generator. Execute imports and the FIRST generator only,
# avoiding a second random-number draw and skipping charts/model training.
marker = '# 1.  SYNTHETIC DATA GENERATION'
first = code.index(marker)
end = code.index('print("✓ Data generation complete")', first)
import numpy as np
import pandas as pd
np.random.seed(42)
scope = {'np': np, 'pd': pd}
begin = code.index('start_date =', first)
exec(compile(code[begin:end], 'notebook_generation', 'exec'), scope)
out = ROOT / 'data'
out.mkdir(exist_ok=True)
tables = {
 'users': ['user_id', 'signup_date', 'city', 'acquisition_channel', 'age_group'],
 'products': ['product_id', 'category', 'base_price'],
 'sessions': ['session_id', 'user_id', 'session_date', 'device', 'traffic_source', 'converted'],
 'orders': ['order_id', 'session_id', 'user_id', 'order_date', 'status', 'delivery_fee',
            'discount', 'delivery_time_min', 'gross_revenue', 'net_revenue'],
 'order_items': ['order_id', 'product_id', 'quantity', 'unit_price', 'item_revenue'],
}
with sqlite3.connect(out / 'foodkadeh.db') as db:
 for name, cols in tables.items():
  frame = scope[name][cols].copy()
  for col in frame.columns:
   if col.endswith('_date'):
    frame[col] = frame[col].dt.strftime('%Y-%m-%d')
  frame.to_sql(name, db, if_exists='replace', index=False)
  frame.to_csv(out / f'{name}.csv', index=False)
 db.executescript((ROOT / 'sql/01_analytics.sql').read_text(encoding='utf-8'))
 for view in ['monthly_kpis', 'channel_conversion', 'customer_rfm', 'cohort_retention', 'category_sales']:
  scope['pd'].read_sql_query(f'SELECT * FROM {view}', db).to_csv(out / f'{view}.csv', index=False)
 expected = scope['completed']['net_revenue'].sum()
 actual = db.execute('SELECT SUM(revenue) FROM monthly_kpis').fetchone()[0]
 assert abs(expected - actual) < 0.01, (expected, actual)
 assert db.execute('SELECT COUNT(*) FROM completed_orders').fetchone()[0] == len(scope['completed'])
 assert db.execute('SELECT COUNT(*) FROM cohort_retention WHERE month_index=0 AND retention_rate<>1').fetchone()[0] == 0
 assert db.execute('SELECT COUNT(*) FROM orders o LEFT JOIN users u USING(user_id) WHERE u.user_id IS NULL').fetchone()[0] == 0
 print(f'Validated: {len(scope["completed"]):,} completed orders; net revenue {actual:,.2f}')
 print(scope['pd'].read_sql_query('SELECT * FROM monthly_kpis', db).to_string(index=False))
