"""Reconcile captured Power BI DAX-query results with regenerated SQL extracts.

This validates the checked-in evidence; it does not connect to Power BI. Recapture
queries through the service UI to verify a later live-model state.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

root=Path(__file__).resolve().parents[1]
evidence=root/'powerbi/validation'
extracts={name:pd.read_csv(root/f'data/PowerBI_{name}.csv') for name in
          ['MonthlyCity','Acquisition','Retention','CustomerSegments','CategorySales']}
live=pd.read_csv(evidence/'live_snapshot_rows.tsv',sep='\t')
live.columns=[c.strip('[]') for c in live.columns]
assert len(live)==78 and not live.duplicated(['Table','Key']).any()
specs={
 'MonthlyCity':(['Month','City'],['NetRevenue','CompletedOrders','DeliveryMinutes','Sessions','ConvertedSessions']),
 'Acquisition':(['Channel','Device'],['Sessions','Conversions']),
 'Retention':(['Cohort','MonthIndex'],['CohortSize','ActiveBuyers']),
 'CustomerSegments':(['Segment'],['Customers','Revenue','Orders','Inactive45','RepeatBuyers']),
 'CategorySales':(['Category'],['Units','Sales']),
}
assert set(live.Table)==set(specs)
for name,(keys,values) in specs.items():
    expected=extracts[name].copy()
    expected['Key']=expected[keys].astype(str).agg('|'.join,axis=1)
    expected=expected.set_index('Key')[values].sort_index()
    expected.columns=list('ABCDE')[:len(values)]
    for c in 'ABCDE':
        if c not in expected:expected[c]=0
    actual=live.loc[live.Table.eq(name)].set_index('Key')[list('ABCDE')].sort_index()
    assert_frame_equal(actual,expected[list('ABCDE')],check_dtype=False,check_exact=False,atol=1e-9,rtol=1e-12)
    print(f'PASS: {name}, all {len(expected)} rows and values match SQL')
m,a,r,s,c=(extracts[n] for n in ['MonthlyCity','Acquisition','Retention','CustomerSegments','CategorySales'])
tehran=m.loc[m.City.eq('Tehran')]
referral=a.loc[a.Channel.eq('Referral') & a.Device.eq('Mobile')]
champions=s.loc[s.Segment.eq('Champions')]
offset1=r.loc[r.MonthIndex.eq(1)]
expected={
 'Net Revenue':m.NetRevenue.sum(), 'Completed Orders':m.CompletedOrders.sum(),
 'Average Order Value':m.NetRevenue.sum()/m.CompletedOrders.sum(),
 'Total Sessions':m.Sessions.sum(), 'Converted Sessions':m.ConvertedSessions.sum(),
 'Session Conversion Rate':m.ConvertedSessions.sum()/m.Sessions.sum(),
 'Average Delivery Minutes':m.DeliveryMinutes.sum()/m.CompletedOrders.sum(),
 'Traffic Sessions':a.Sessions.sum(), 'Traffic Conversions':a.Conversions.sum(),
 'Traffic Conversion Rate':a.Conversions.sum()/a.Sessions.sum(),
 'Segment Buyers':s.Customers.sum(), 'Segment Revenue':s.Revenue.sum(),
 'Revenue per Buyer':s.Revenue.sum()/s.Customers.sum(),
 'Repeat Buyer Rate':s.RepeatBuyers.sum()/s.Customers.sum(),
 'Inactive Buyer Rate':s.Inactive45.sum()/s.Customers.sum(),
 'Product Sales':c.Sales.sum(), 'Product Units':c.Units.sum(), 'Category Sales Share':1,
 'Category selection share':1,
 'Champions repeat rate':champions.RepeatBuyers.sum()/champions.Customers.sum(),
 'Cohort total blank':'', 'Cohort future February month 1':'',
 'Cohort month 0':1, 'Cohort month 1':offset1.ActiveBuyers.sum()/offset1.CohortSize.sum(),
 'Cohort September month 1':5/30,
 'Tehran revenue':tehran.NetRevenue.sum(), 'Tehran orders':tehran.CompletedOrders.sum(),
 'Tehran AOV':tehran.NetRevenue.sum()/tehran.CompletedOrders.sum(),
 'Tehran conversion':tehran.ConvertedSessions.sum()/tehran.Sessions.sum(),
 'Tehran delivery':tehran.DeliveryMinutes.sum()/tehran.CompletedOrders.sum(),
 'September revenue':m.loc[m.Month.eq('2025-09'),'NetRevenue'].sum(),
 'Referral Mobile conversion':referral.Conversions.sum()/referral.Sessions.sum(),
 'Revenue display':f'${m.NetRevenue.sum():,.2f}', 'Orders display':f'{m.CompletedOrders.sum():,}',
 **{f'Rows {name}':len(df) for name,df in extracts.items()},
}
checks=pd.read_csv(evidence/'live_measures.tsv',sep='\t',keep_default_na=False)
assert len(checks)==39 and not checks['[Check]'].duplicated().any()
assert set(checks['[Check]'])==set(expected)
for row in checks.itertuples(index=False,name=None):
    name,kind,value=row
    if kind=='Number':assert np.isclose(float(value),expected[name],atol=1e-9,rtol=1e-12),(name,value,expected[name])
    else:assert value==expected[name],(name,value,expected[name])
pair=c.loc[c.Category.isin(['Restaurant Meal','Grocery'])].set_index('Category')
pair['Share']=pair.Sales/pair.Sales.sum()
actual=pd.read_csv(evidence/'live_category_share.tsv',sep='\t').set_index('CategorySales[Category]')
assert set(actual.index)==set(pair.index)
assert np.allclose(actual['[ProductSales]'],pair.reindex(actual.index).Sales,atol=1e-9,rtol=1e-12)
assert np.allclose(actual['[Share]'],pair.reindex(actual.index).Share,atol=1e-9,rtol=1e-12)
print('PASS: all 39 measure/count/filter checks; both filtered category sales/share rows')
