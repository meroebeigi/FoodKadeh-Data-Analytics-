# FoodKadeh Data Analytics

A comprehensive data analytics notebook for FoodKadeh, an online food-commerce platform. This project simulates and analyzes customer behavior, acquisition efficiency, retention patterns, and operational performance using Python, Pandas, and Scikit-learn.

---

## 📋 Project Overview

**FoodKadeh** is a food delivery and food-commerce platform operating across major Iranian cities (Tehran, Shiraz, Isfahan, Tabriz, Mashhad). This analytics project examines 6 months of synthetic transaction data (Sep 2025 – Feb 2026) covering:

- **2,500 customers** from multiple acquisition channels
- **22,000 sessions** across multiple devices
- **1,506 completed orders** across 6 product categories
- **Revenue of $72,431** with insights into profitability drivers

The notebook combines business intelligence, statistical analysis, machine learning, and operational insights to answer key questions about growth, customer value, retention, and churn.

---

## 🎯 Key Questions & Analysis Sections

### 1. **What kind of business scenario are we simulating for FoodKadeh?**
   - Synthetic data generation for a realistic food-commerce business
   - Multi-city operation with diverse customer segments
   - Real-world patterns: sign-ups grow over time, channels vary in efficiency, delivery times fluctuate
   - Foundation for prototyping analytics without private company data

### 2. **What is the overall health of FoodKadeh at a glance?**
   - **Executive KPI Dashboard** with metrics:
     - Total Revenue: $72,431
     - Completed Orders: 1,506
     - Average Order Value (AOV): $48.10
     - Total Users: 2,500
     - Conversion Rate: 17.3%
     - Repeat Rate: 32%

### 3. **How are FoodKadeh's revenue, orders, and average order value changing over time?**
   - **Sales KPI Trends** analysis with:
     - Daily and monthly revenue tracking
     - 7-day rolling averages to smooth noise
     - Order volume trends
     - AOV stability analysis
   - **Key Finding:** Growth is order-volume driven, not price-driven (AOV is flat)
   - **Action Items:** Focus on upselling, bundling, and customer retention

### 4. **Which acquisition channels and devices are bringing the best customers?**
   - **Customer Acquisition Analysis:**
     - Referral: 23.8% conversion rate (highest quality)
     - Direct: 21.1% conversion rate
     - Organic Search: 16.5% conversion rate (highest volume)
     - Google Ads: 15.9% conversion rate
     - Instagram Ads: 14.1% conversion rate (lowest efficiency)
   - **Device Performance:** Mobile dominates (78% of sessions) but Desktop converts better
   - **Key Finding:** High traffic ≠ high performance; referral is the most efficient channel
   - **Action Items:** Scale referral programs, optimize paid ads for conversion

### 5. **Which customer groups are most valuable, loyal, or at risk?**
   - **RFM Segmentation** (Recency, Frequency, Monetary):
     - Champions: 235 customers, $124 avg revenue (core revenue drivers)
     - Loyal: 264 customers, steady repeat behavior
     - Potential Loyalists: 171 customers (growth opportunity)
     - New Customers: High recent activity
     - At Risk: 226 customers with declining engagement
     - Lost: Customers beyond recovery threshold
   - **Key Finding:** Revenue is concentrated in high-value segments; majority of users are low-value
   - **Action Items:** Personalize campaigns by segment; upgrade low-value to regular/VIP

### 6. **Are there natural customer groups beyond manually defined RFM segments?**
   - **K-Means Clustering** with behavioral features:
     - VIP Cluster: 235 customers, $124 avg revenue, high frequency & spending
     - Regular Cluster: 221 customers, $104 avg revenue, mid-tier engagement
     - Low-Value Cluster: 475 customers, $34 avg revenue (largest but least profitable)
     - Inactive Cluster: 116 customers, minimal engagement
   - **Optimal Number of Clusters:** 4 (determined via elbow method)
   - **Key Finding:** Clear behavioral separation; opportunity to move users up the value ladder
   - **Action Items:** Implement tiered loyalty system, segment-driven personalization

### 7. **Which customers are likely to stop ordering, and what can FoodKadeh do about it?**
   - **Churn Prediction Models:**
     - Logistic Regression: 77% accuracy, ROC-AUC: 0.77
     - Random Forest: 81% accuracy, ROC-AUC: 0.81 (best performer)
   - **Top Churn Drivers (Feature Importance):**
     1. Recency (days since last order) - strongest predictor
     2. Total orders
     3. Total revenue
     4. Order frequency
     5. Customer tenure
   - **Churn Definition:** No orders in 45+ days
   - **Key Finding:** Churn is behavioral and predictable; recency dominates
   - **Action Items:** Build early warning system at 7/14/21+ day thresholds; trigger targeted interventions

### 8. **Which products, cities, and operational factors have the biggest impact on performance?**
   - **Product Category Performance:**
     - Restaurant Meals: 53.1% of revenue (core business)
     - Grocery: 29.0% of revenue (strong secondary)
     - Bakery, Healthy Food, Snack, Beverage: 10.9% combined
   - **City Performance:**
     - Tehran: Highest volume, ~$46 AOV
     - Mashhad: Highest AOV (~$55), premium customer segment
     - Isfahan: Lowest AOV (~$46), slowest delivery (37.9 min)
   - **Demographic Insights:**
     - Age 45-54: Highest AOV ($52.12)
     - Age 18-24: Lower AOV but volume players
   - **Delivery Efficiency:**
     - Average: 36-38 minutes across cities
     - Isfahan slowest; Shiraz fastest
   - **Key Finding:** Operations and marketing should be localized; delivery time is a friction point
   - **Action Items:** City-level strategies, delivery optimization, demographic targeting

### 9. **Are customers staying with FoodKadeh after their first purchase?**
   - **Retention & Repeat Purchase Analysis:**
     - One-time buyers: Large majority (low repeat rate)
     - Occasional (2-3 orders): Moderate segment
     - Regular (4-6 orders): Smaller engaged group
     - Loyal (7+ orders): Very small but high-value core
   - **Cohort Retention Heatmap:** Shows monthly cohorts and return behavior over time
   - **Early Drop-Off:** Sharpest decline immediately after first purchase (Month 0)
   - **Key Finding:** Acquisition is strong but early retention is weak; most customers don't return
   - **Action Items:** Focus on first 7 days post-purchase; second-order incentives; habit-building campaigns

---

## 💡 Business Model & Strategy

### Current Business Model
FoodKadeh operates as a **multi-category food-commerce marketplace** with:

- **Primary Model:** Order-volume acquisition model (growth through new customers)
- **Secondary Model:** Delivery + marketplace commission on orders
- **Revenue Driver:** Order volume, not order value (AOV stable at ~$48)
- **Acquisition Mix:** Paid ads (43%), organic (32%), referral (14%), direct (10%)
- **Customer Base:** Young to middle-aged urban professionals in major Iranian cities

### Strategic Insights

**Strengths:**
- Strong conversion rate (17.3% vs. industry 10-20%)
- High-performing channels (Referral 24%, Direct 21%)
- Rapid user acquisition (287 → 575 new users/month)
- Stable pricing model (consistent AOV)

**Weaknesses:**
- Low repeat rate (32%) - most customers one-time buyers
- High churn risk - retention not yet optimized
- Geographic fragmentation - operations not localized
- Delivery efficiency varies by city (35.9-37.9 min)
- Low-value customer segment dominates (475/1,047 = 45%)

**Opportunities:**
- **Retention Focus:** Moving users from 1-time → repeat → loyal (highest ROI)
- **AOV Optimization:** Bundles, upselling, free-delivery thresholds (target: $48 → $55+)
- **Localization:** City-level pricing, product, and delivery strategies
- **Referral Scaling:** Highest-performing channel; expand program
- **Operational:** Reduce delivery times, improve customer experience

### Recommended Growth Path

1. **Phase 1 (Immediate):** Improve first-purchase experience → second-order conversion
2. **Phase 2 (3–6 months):** Build retention loops → increase repeat rate to 40%+
3. **Phase 3 (6–12 months):** AOV optimization via bundles and upselling
4. **Phase 4 (12+ months):** Shift to customer lifetime value maximization, reduce CAC dependency

---

## 🛠️ Skills Developed

### Data Science & Analysis
- **Data Generation & Simulation:** Creating realistic synthetic datasets with Python/NumPy
- **Exploratory Data Analysis (EDA):** Pandas for data wrangling, aggregation, and summarization
- **Statistical Analysis:** Cohort analysis, retention curves, trend decomposition
- **Time Series Analysis:** Daily/monthly KPI tracking, rolling averages, seasonality detection

### Machine Learning
- **Segmentation:** K-means clustering with feature engineering and optimal cluster selection
- **Predictive Modeling:** Logistic Regression and Random Forest for churn classification
- **Model Evaluation:** ROC curves, confusion matrices, AUC-ROC, feature importance analysis
- **Data Preprocessing:** Standard scaling, categorical encoding, train-test splitting

### Business Intelligence
- **KPI Definition & Calculation:** Revenue metrics, conversion rates, retention, churn, LTV, CAC
- **Dashboard Design:** Executive summaries, multi-panel visualizations, heatmaps
- **Segmentation Strategy:** RFM analysis, behavioral clustering, cohort tracking
- **Insights to Action:** Translating analysis into business recommendations

### Data Visualization
- **Python/Matplotlib:** Custom styling with brand color palette
- **Multi-panel Figures:** GridSpec for complex layouts
- **Advanced Charts:** Cohort heatmaps, dual-axis plots, donut charts, ROC curves
- **Professional Design:** Dark theme, readable typography, effective color use

### Python Libraries & Tools
- **Pandas:** Data manipulation, groupby aggregations, merging, pivot tables
- **NumPy:** Array operations, random sampling, numerical computations
- **Scikit-learn:** KMeans, LogisticRegression, RandomForest, train_test_split, preprocessing
- **Matplotlib:** Publication-quality visualizations with custom styling
- **Jupyter Notebooks:** Interactive analysis and documentation

---

## 📊 Key Metrics & KPIs

| Metric | Value | Status | Action |
|--------|-------|--------|--------|
| **Total Revenue** | $72,431 | Growing | Maintain |
| **Completed Orders** | 1,506 | Growing | Scale |
| **Average Order Value** | $48.10 | Flat | Improve via upselling |
| **Conversion Rate** | 17.3% | Strong | Maintain |
| **Repeat Rate** | 32% | Weak | **Priority:** Improve to 40%+ |
| **Churn Rate** | 68% | High | **Priority:** Implement early warning |
| **Top Channel (Referral)** | 23.8% CVR | Excellent | Scale referral program |
| **Mobile Dominance** | 78% sessions | High | Optimize mobile UX |
| **Restaurant Meals** | 53.1% revenue | Concentrated | Diversify; cross-sell |
| **Delivery Time** | 36-38 min | High | Reduce by 5-10% |

---

## 📈 How to Use This Notebook

### Prerequisites
- Python 3.8+
- Jupyter Notebook or JupyterLab
- Required libraries: `numpy`, `pandas`, `matplotlib`, `scikit-learn`

### Installation
```bash
# Clone or download the repository
cd FoodKadeh-DataAnalytics

# Install dependencies
pip install numpy pandas matplotlib scikit-learn

# Launch Jupyter Notebook
jupyter notebook FoodKadeh.ipynb
```

### Workflow
1. **Run Section 1** to generate synthetic data (reproducible with RANDOM_STATE=42)
2. **Run Sections 2-3** for executive KPI dashboard
3. **Run Sections 4-5** for acquisition and segmentation analysis
4. **Run Section 6** for churn prediction models
5. **Run Sections 7-9** for operational and retention insights
6. **Review strategy sections** for actionable recommendations per segment

### Customization
- **Adjust time period:** Modify `start_date` and `end_date` in Section 1
- **Change user counts:** Update `n_users` and `n_sessions` to scale data
- **Modify channels/categories:** Edit lists in Section 1 for your business
- **Connect real data:** Replace synthetic data generation with your actual database queries
- **Tune model parameters:** Adjust KMeans clusters, Random Forest depth, churn threshold (45 days)

---

## 🔗 Next Steps & Integration

### To Connect Real Data
1. Replace Section 1 data generation with SQL queries to your database
2. Ensure column names match: `user_id`, `order_id`, `order_date`, `status`, `net_revenue`, etc.
3. Run remaining sections unchanged

### To Deploy to Production
1. Convert notebook cells to Python functions in `analytics.py`
2. Schedule daily/weekly runs via cron or cloud scheduler
3. Store results in a data warehouse or BI tool (Tableau, Looker, Power BI)
4. Create dashboards for stakeholders

### To Expand Analysis
- Add geographic heat maps (city-level performance)
- Implement A/B testing framework for campaigns
- Build customer recommendation engine
- Create dynamic pricing model by segment
- Add competitive benchmarking

---

## 📂 File Structure

```
FoodKadeh-DataAnalytics/
├── README.md                          # This file
├── FoodKadeh.ipynb                    # Main Jupyter Notebook with all analysis
└── (Optional: future modules)
    ├── data_loader.py                 # Connect to real database
    ├── analytics_functions.py         # Reusable analysis functions
    └── visualizations.py              # Custom plotting utilities
```

---

## 📝 Analysis Sections Summary

| Section | Type | Output | Key Finding |
|---------|------|--------|------------|
| 1. Data Generation | Setup | Synthetic tables | Foundation ready |
| 2. KPI Overview | Executive | Dashboard card | $72.4K revenue, 32% repeat |
| 3. Sales Trends | Analysis | Time series charts | Order-driven growth |
| 4. Acquisition | Analysis | Channel comparison | Referral best (24% CVR) |
| 5. RFM Segmentation | Segmentation | 6 segments | VIP is 23% of customers, 39% of revenue |
| 6. K-Means Clustering | ML | 4 clusters | VIP/Regular/Low-value/Inactive |
| 7. Churn Prediction | ML | RF model (81% AUC) | Recency is strongest signal |
| 8. Operational Insights | Analysis | 4 operational views | Restaurant 53% revenue; delivery 36-38 min |
| 9. Retention | Analysis | Cohort heatmap | Early drop-off; majority one-time |

---

## 🤝 Contributing & Feedback

This is a prototype analytics framework. To improve it:
- Add real transaction data
- Implement additional models (propensity scoring, RFM-RF hybrid)
- Expand to more cities and product categories
- Connect to your BI platform

---

## 📞 Contact & Support

For questions or feedback on this analysis:
- Review the strategy sections within each analysis
- Check the notebook's detailed commentary for each finding
- Refer to the KPI definition table for metric explanations

---

## 📜 License

This project is provided as-is for educational and business intelligence purposes.

---

## 🎓 Key Takeaways

**FoodKadeh is performing well on acquisition and conversion, but must prioritize retention to build a sustainable, profitable business.**

The path forward:
1. **Reduce churn** via early warning system
2. **Increase repeat rate** from 32% → 40%+
3. **Improve AOV** from $48 → $55+ via bundles
4. **Localize strategy** by city and segment
5. **Shift from volume to value:** Maximize customer lifetime value

With these improvements, FoodKadeh can transition from an acquisition-driven model to a retention-and-value-driven model, significantly improving profitability and unit economics.

---

**Last Updated:** June 2026  
**Data Period:** Sep 2025 – Feb 2026  
**Analysis Type:** Synthetic Data Prototype (Ready for Real Data Integration)
