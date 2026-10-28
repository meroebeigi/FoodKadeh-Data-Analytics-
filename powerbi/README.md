# Power BI analytics portfolio

Source assets for building a FoodKadeh report: [DAX measures](measures.dax), [Power Query CSV loader](import_csv.pq), and a [brand theme](theme.json). These newly added assets demonstrate semantic modeling, filter context, reusable transformations, time intelligence, and KPI design. No completed `.pbix`, published report, or Power BI screenshots are included yet. Existing root PNGs are Python charts.

## Build the model

1. Run `python scripts/export_analytics.py` from the repository root (see [SQL setup](../sql/README.md)).
2. In Power BI Desktop, import `users.csv`, `orders.csv`, `sessions.csv`, `products.csv`, and `order_items.csv` from `data/`. Name tables Users, Orders, Sessions, Products, and OrderItems. Use the reusable M function or Text/CSV import. Set IDs and quantity/converted to whole numbers, dates to Date, financial fields to fixed decimal, delivery time to decimal, and remaining fields to text. The M file contains a complete Orders invocation example.
3. Create one-to-many, single-direction relationships: Users[user_id] → Orders[user_id]; Users[user_id] → Sessions[user_id]; Orders[order_id] → OrderItems[order_id]; Products[product_id] → OrderItems[product_id]. Do not add a Sessions-to-Orders relationship: it creates a second filter path.
4. Create the Date calculated table from `measures.dax`, mark Date[Date] as its date column, and connect Date[Date] → Orders[order_date] and Date[Date] → Sessions[session_date]. Keep Users[signup_date] unrelated for this report. Add each measure separately; format money to 2 decimals and ratios as percentages.
5. Import `theme.json`. Label currency as synthetic dollars, matching the notebook; this is not a verified local-currency conversion.

## Report pages and interactions

| Page | Visuals | Business decision |
| --- | --- | --- |
| Executive overview | Net Revenue, Completed Orders, AOV, Repeat Purchase Rate cards; monthly revenue/orders trends | Monitor growth and repeat buying |
| Acquisition | Sessions and Session Conversion Rate by Sessions[traffic_source] and device | Compare traffic quality |
| Customer value | Import customer_rfm.csv as a separate snapshot table; segment counts and monetary value | Prioritize retention campaigns |
| Retention | Import cohort_retention.csv separately; matrix of cohort × month_index with retention_rate and conditional formatting | Identify early drop-off |
| Products and operations | Product Sales by category; Average Delivery Minutes and AOV by Users[city] | Compare category mix and delivery |

Use date and city slicers on transactional pages. Session traffic source differs from Users[acquisition_channel]; label them distinctly. A session-source slicer does not filter Orders in this model. Disable date/city slicer interactions on the two disconnected snapshot pages; title them “Full-period snapshot — through Feb 2026.” Use the SQL-exported retention rate without summing percentages; each matrix cell must contain exactly one cohort/month row. Future cells remain blank.

Product filters apply to OrderItems, so use Product Sales for category visuals. Net Revenue remains an order-level measure and must not be presented as category net revenue. Repeat Purchase Rate is calculated within the selected transaction period, not lifetime. MoM comparisons are intended for complete calendar months; suppress or clearly label partial-month comparisons.

## Validate before presenting

- Match the unfiltered Completed Orders and Net Revenue cards to exporter output and SQL monthly totals.
- Check a single month and city against a direct completed-order aggregation, then reset slicers.
- Check conversion numerator/denominator against channel_conversion.csv for a chosen source/device.
- Confirm cohort Month 0 is 100%, observed inactive months show 0%, and future months are blank.
- Confirm category Product Sales totals match SQL category_sales; compare with item revenue, not order net revenue.
- Check cross-filter behavior, empty selections, percentage formats, accessible contrast, and tooltip definitions.

Save the verified report as `FoodKadeh.pbix` in this folder and add actual screenshots/exported pages when built. DAX/M assets have not been executed in Power BI during this update; no service publication or refresh schedule is claimed.
