"""Check source integrity, SQL/Pandas agreement and the shipped report structure.

Run after the exporter and both prepare_powerbi_* scripts. Does not decode the
binary VertiPaq model or query the Power BI service; see CONSISTENCY_REVIEW.md.
"""
import json
import sqlite3
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from foodkadeh_data import generate_data, analytics_view

ROOT = Path(__file__).resolve().parents[1]
data = ROOT / 'data'
tables = generate_data(42)
again = generate_data(42)
for name in ['users', 'products', 'sessions', 'orders', 'order_items']:
    assert_frame_equal(tables[name], again[name])
users, sessions, orders, items = (tables[n] for n in ['users', 'sessions', 'orders', 'order_items'])
completed = tables['completed']
for name, key in [('users','user_id'),('products','product_id'),('sessions','session_id'),('orders','order_id')]:
    assert not tables[name][key].duplicated().any(), (name, 'duplicate primary key')
for child, key, parent in [('sessions','user_id','users'),('orders','user_id','users'),
                          ('orders','session_id','sessions'),('order_items','order_id','orders'),
                          ('order_items','product_id','products')]:
    assert tables[child][key].isin(tables[parent][key]).all(), (child, key, 'orphan')
assert not items.duplicated(['order_id','product_id']).any()
assert (sessions.session_date >= sessions.signup_date).all()
assert set(orders.session_id) == set(sessions.loc[sessions.converted.eq(1), 'session_id'])
item_sales = items.groupby('order_id').item_revenue.sum()
sales = completed.set_index('order_id')
assert np.allclose(sales.net_revenue, item_sales.reindex(sales.index) + sales.delivery_fee - sales.discount)
assert orders.loc[orders.status.ne('Completed'), 'net_revenue'].eq(0).all()
with sqlite3.connect(data/'foodkadeh.db') as db:
    for view in ['monthly_kpis','customer_rfm','cohort_retention','channel_conversion','category_sales']:
        expected = analytics_view(tables, view)
        actual = pd.read_sql_query(f'SELECT * FROM {view}', db)
        assert_frame_equal(actual, expected, check_dtype=False, check_exact=False, atol=1e-9, rtol=1e-12)
monthly = pd.read_csv(data/'PowerBI_MonthlyCity.csv')
assert len(monthly)==30 and not monthly.duplicated(['Month','City']).any()
assert round(monthly.NetRevenue.sum(),2)==72431.22
assert monthly.CompletedOrders.sum()==1506
assert monthly.Sessions.sum()==9838 and monthly.ConvertedSessions.sum()==1698
assert abs(monthly.DeliveryMinutes.sum()/1506-completed.delivery_time_min.mean())<1e-9
assert round(monthly.loc[monthly.City.eq('Tehran'),'NetRevenue'].sum(),2)==33557.59
rfm = analytics_view(tables,'customer_rfm')
segments = pd.read_csv(data/'PowerBI_CustomerSegments.csv').set_index('Segment').sort_index()
rfm['Inactive45'] = rfm.recency_days.gt(45).astype(int)
rfm['RepeatBuyers'] = rfm.frequency.gt(1).astype(int)
expected = rfm.groupby('segment').agg(Customers=('user_id','size'), Revenue=('monetary','sum'),
                                     Orders=('frequency','sum'), Inactive45=('Inactive45','sum'),
                                     RepeatBuyers=('RepeatBuyers','sum'))
expected.Revenue = expected.Revenue.round(2)
expected.index.name = 'Segment'
assert_frame_equal(segments,expected,check_dtype=False)
assert segments.Customers.sum()==1047 and segments.Inactive45.sum()==442 and segments.RepeatBuyers.sum()==335
assert segments.Customers.to_dict()=={'At Risk':224,'Champions':138,'Lost':100,'Loyal':265,'New Customers':148,'Potential Loyalists':172}
cohorts = pd.read_csv(data/'PowerBI_Retention.csv')
assert not cohorts.duplicated(['Cohort','MonthIndex']).any()
assert (cohorts.loc[cohorts.MonthIndex.eq(0),'ActiveBuyers'].to_numpy()==cohorts.loc[cohorts.MonthIndex.eq(0),'CohortSize'].to_numpy()).all()
assert (pd.to_datetime(cohorts.Cohort).dt.year*12 + pd.to_datetime(cohorts.Cohort).dt.month + cohorts.MonthIndex <= 2026*12+2).all()
# Independently reconstruct observed cohort cells with Pandas, including zero activity.
purchases=completed[['user_id','order_date']].drop_duplicates().copy()
purchases['Cohort']=purchases.groupby('user_id').order_date.transform('min').dt.to_period('M')
purchases['MonthIndex']=(purchases.order_date.dt.year-purchases.Cohort.dt.year)*12+purchases.order_date.dt.month-purchases.Cohort.dt.month
active=purchases.groupby(['Cohort','MonthIndex']).user_id.nunique()
sizes=purchases.groupby('Cohort').user_id.nunique()
for row in cohorts.itertuples():
    key=(pd.Period(row.Cohort,freq='M'),row.MonthIndex)
    assert row.ActiveBuyers==active.get(key,0) and row.CohortSize==sizes.loc[key[0]]
acq = pd.read_csv(data/'PowerBI_Acquisition.csv')
expected = sessions.groupby(['traffic_source','device']).agg(Sessions=('session_id','size'),Conversions=('converted','sum'))
actual = acq.set_index(['Channel','Device']).sort_index();actual.index.names=expected.index.names
assert_frame_equal(actual,expected,check_dtype=False)
categories = pd.read_csv(data/'PowerBI_CategorySales.csv').set_index('Category').sort_index()
expected = analytics_view(tables,'category_sales').rename(columns={'category':'Category','units':'Units','product_sales':'Sales'}).set_index('Category')[['Units','Sales']].sort_index()
expected.Sales=expected.Sales.round(2)
assert_frame_equal(categories,expected,check_dtype=False)
with zipfile.ZipFile(ROOT/'powerbi/FoodKadeh.pbix') as z:
    assert z.testzip() is None
    pages=[json.loads(z.read(n)) for n in z.namelist() if n.endswith('/page.json')]
    assert {p['displayName'] for p in pages}=={'Overview','Monthly detail','City scorecard','Acquisition','Customer value','Retention','Products'}
    assert all((p['width'],p['height'])==(1280,720) for p in pages)
    assert sum(n.endswith('/visual.json') for n in z.namelist())==13
    assert len(z.read('DataModel'))>0
nb=json.loads((ROOT/'FoodKadeh.ipynb').read_text(encoding='utf-8'))
code=[c for c in nb['cells'] if c['cell_type']=='code']
assert all(c['execution_count'] is not None for c in code), 'Run all notebook cells before publishing'
assert not any(o.get('output_type')=='error' for c in code for o in c['outputs'])
assert sum('tables = generate_data(RANDOM_STATE)' in ''.join(c['source']) for c in code)==1
print('PASS: deterministic data, source integrity, five SQL views, all report extracts, seven PBIX pages, 13 visuals, executed notebook.')
