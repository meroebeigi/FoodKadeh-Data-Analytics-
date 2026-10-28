# Cross-layer consistency review — 28 October 2026

Scope: all repository READMEs, Python generation/export code, SQL views, Jupyter code and saved outputs, eight root chart images, implemented/template DAX, Power Query, themes and the shipped PBIX. The report and dashboard links refer to the existing account-owned Power BI service objects.

## Findings and corrections

| Finding | Correction |
| --- | --- |
| Notebook generated the dataset twice, consuming a second random draw; exporter parsed only its first generator | One shared `generate_data(seed=42)` function; notebook and exporter each call it once. The original first draw and published report totals are preserved. |
| README treated 22,000 candidate sessions as analyzed sessions | Distinguish candidates from the 9,838 retained post-signup sessions. |
| Notebook RFM used Pandas qcut while SQL/Power BI used NTILE | Notebook now evaluates the same SQL RFM view with deterministic user-ID tie breaks. Six segment counts match the report. |
| Cohort pivot could show a missing observed activity cell as blank | Notebook uses the SQL cohort grid: observed inactivity zero, future months absent/blank. |
| KPI section called repeat buying retention and its complement churn | Explicit repeat/non-repeat buyer rates; current 45-day inactivity is a separate 442/1,047 (42.2%) measure. Internal classifier target renamed `inactive45`. |
| Final KPI delivery average included non-completed orders | Completed orders only, matching report/SQL definitions. |
| Observed total purchase frequency was multiplied by an observed month span and called LTV | LTV unavailable: a six-month purchase history does not establish future lifetime. Gross margin, CAC and LTV/CAC also remain unavailable. |
| Fixed README AUCs, recency-importance claim, future-churn language | Regenerated outputs give LR AUC 0.700 and RF AUC 0.653. Recency defines the current inactivity label but is excluded from inputs. Random holdout performance does not validate future churn forecasting. |
| Claims about mobile trailing desktop, highest city delivery time, ROI, campaign causes and precise improvement effects were unsupported | Use computed descriptive tables and label business actions as experiments. No cost, campaign, SLA or causal-impact estimates are claimed. |
| Exporter could retain outdated view definitions through CREATE VIEW IF NOT EXISTS | Exporter drops/recreates its analytical views on each run. |
| Images, cached outputs and documentation could describe different runs | Executed all 16 code cells, regenerated 10 figures and replaced root 1.png–8.png; updated all READMEs. Fixed confusion-matrix text contrast. |

## Verification

The shared generation reproduces 2,500 users, 120 products, 9,838 sessions, 1,698 orders, 1,506 completed orders, 1,047 buyers and **72,431.22** net revenue. Repeat buyers are 335; inactive buyers are 442. Product units total 3,899.

`scripts/validate_consistency.py` passes deterministic reruns, source primary keys and foreign keys, session/signup ordering, converted-session/order agreement, item-to-order revenue reconciliation, five exported SQL views, all five report-input extracts and independent Pandas acquisition/cohort aggregations. It also checks executed notebook status, the PBIX ZIP, seven named HD pages, 13 visuals and an embedded model. The notebook's final cell reconciles its executed outputs to SQL.

Notebook execution used Python 3.12, NumPy 2.5.4, Pandas 3.0.1, Matplotlib 3.11.2 and scikit-learn 1.9.1. Dependencies are pinned in `requirements.txt`. The canonical generator/export was also checked with the existing NumPy 2.3.5 environment and returned the same published totals. The notebook was executed cell by cell through IPython with captured text/rich outputs; regenerated KPI/model charts were visually inspected.

The published Power BI figures remain valid for this preserved snapshot. Its PBIX and existing service objects require no data changes for these consistency repairs. It contains five disconnected static SQL snapshots, not the five full transaction tables and not a live OneDrive workbook connection. Transaction-level DAX/relationships in the guide remain optional templates.

## Verification limits

- PBIX checks inspect report JSON and archive integrity; the binary VertiPaq model is not decoded or refreshed by the validation script. Agreement with embedded snapshot values relies on the service checks performed when the report was authored and the preserved canonical dataset. The script does not automate a Power BI service query.
- Classifier evaluation is a random buyer holdout on synthetic current-inactivity labels. There is no temporal future-outcome validation, causal estimate, or production-performance claim.
- The dashboard is a separate service object. It is not embedded in the PBIX; live dashboard availability and account permissions cannot be established by local file checks.
