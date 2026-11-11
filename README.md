<h1 align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=30&pause=1000&color=0C0F5E&center=true&vCenter=true&width=850&lines=SignalSentinel+AI;Intelligent+Business+Early-Warning+System&height=100" alt="SignalSentinel AI" />
</h1>

<h3 align="center">
  Detecting Sales Anomalies • Monitoring Business Risk • Generating Insights
</h3>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  </a>
  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white">
  </a>
  <a href="https://pandas.pydata.org/">
    <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white">
  </a>
  <a href="https://scikit-learn.org/">
    <img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white">
  </a>
  <a href="https://powerbi.microsoft.com/">
    <img src="https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black">
  </a>
</p>

## SignalSentinel AI
### Intelligent Business Early-Warning System

**SignalSentinel AI** is a data analytics and machine learning project designed to identify unusual sales behaviour, detect potential store-level sales declines, and highlight business patterns that may require further investigation.

The project combines Python, SQL, Machine Learning, and Power BI to transform historical retail sales data into actionable business insights.

---

## 1. Project Objective

Retail businesses generate large volumes of daily sales data. Identifying unusual changes, understanding sales patterns, and detecting potential performance issues across multiple stores can be challenging.

SignalSentinel AI addresses this problem by:

- Monitoring historical sales performance.
- Identifying unusual sales patterns using statistical analysis.
- Detecting potential store-level sales declines.
- Comparing rule-based alerts with machine learning detections.
- Investigating weekday, monthly, and calendar-related patterns.
- Presenting findings through an interactive Power BI dashboard.

**Business Goal:** Build an analytical system that helps business teams identify unusual sales behaviour and prioritize areas for investigation.

---

## 2. Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Data Analysis | Pandas, NumPy |
| Database | PostgreSQL |
| Machine Learning | Scikit-learn, Isolation Forest |
| Visualization | Matplotlib, Power BI |
| Data Processing | SQL, Python |
| Development Tools | VS Code, Jupyter Notebook, Git, GitHub |

---

## 3. Dataset

The project uses the **M5 Forecasting Accuracy dataset**, based on Walmart retail sales.

The dataset contains historical product-level sales information across multiple stores.

### Dataset Components

| File | Description |
|---|---|
| sales_train_validation.csv | Historical daily product sales |
| calendar.csv | Calendar information, weekdays, events, and dates |
| sell_prices.csv | Product selling prices across stores |

### Dataset Overview

- 30,490 product-store sales series.
- 10 retail stores.
- 3,049 products.
- 1,913 historical daily sales observations per series.
- Historical period: January 2011 – April 2016.

The dataset provides the foundation for sales analysis, anomaly detection, and store-level performance monitoring.

---

## 4. Project Architecture

```text
SignalSentinel-AI/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── src/
│   ├── analyze_daily_sales.py
│   ├── analyze_weekly_patterns.py
│   ├── analyze_monthly_patterns.py
│   ├── analyze_year_end_patterns.py
│   ├── detect_store_declines.py
│   ├── detect_weekday_anomalies.py
│   └── detect_ml_anomalies.py
│
├── sql/
│
├── dashboards/
│   └── SignalSentinel AI.pbix
│
├── models/
│   └── isolation_forest_weekday_adjusted.pkl
│
├── reports/
│   ├── daily_sales_totals.csv
│   ├── monthly_sales_summary.csv
│   ├── yearly_sales_summary.csv
│   ├── weekday_sales_summary.csv
│   ├── store_decline_analysis.csv
│   ├── weekday_adjusted_anomalies.csv
│   ├── ml_anomaly_weekday_adjusted_test.csv
│   ├── ml_anomaly_weekday_summary.csv
│   ├── model_comparison_summary.csv
│   └── model_evaluation_summary.md
│
└── README.md
```

---

## 5. Data Analysis and Business Insights

### Daily Sales Analysis

Analyzed daily sales performance across the historical dataset.

Key findings:
- Average daily sales: approximately 34,342 units.
- Highest observed daily sales: 57,218 units.
- Lowest observed daily sales: 11 units.
- Identified substantial variation in daily sales activity.

### Weekly Sales Patterns

Analyzed sales behaviour across different weekdays.

Key findings:
- Saturday average sales: approximately 41,547 units.
- Sunday average sales: approximately 41,130 units.
- Wednesday average sales: approximately 30,010 units.
- Saturday sales were approximately 38.4% higher than Wednesday sales.

### Monthly Sales Patterns

Analyzed monthly average daily sales to identify seasonal variations.

Key findings:
- August recorded the highest average daily sales.
- May recorded the lowest average daily sales.
- The difference between these monthly averages was approximately 10.6%.

### Calendar and Year-End Investigation

Investigated unusual sales patterns around holidays and calendar events.

Key findings:
- December 25 recorded exceptionally low sales across the observed years.
- December 2014 showed multiple simultaneous store-level decline alerts.
- Calendar patterns were investigated without assuming that recorded events directly caused the observed sales changes.

---

## 6. Rule-Based Store Decline Detection

Developed a rule-based monitoring approach to identify potential store-level sales declines.

### Detection Logic

The system compares:

- Recent 7-day average sales.
- Previous 28-day average sales.

A potential decline alert is generated when the recent average is at least 15% below the previous 28-day average.

### Results

| Metric | Result |
|---|---:|
| Stores monitored | 10 |
| Store-day records analyzed | 18,790 |
| Potential decline alerts | 720 |
| Alert rate | 3.83% |

The 15% threshold is exploratory and has not been independently validated.

---

## 7. Statistical Anomaly Detection

Developed weekday-adjusted statistical anomaly detection using historical sales patterns.

### Methodology

- Calculated historical averages for the same weekday.
- Compared actual sales against the weekday baseline.
- Used historical standard deviation to calculate anomaly scores.
- Applied a threshold of absolute Z-score greater than 3.

### Results

| Metric | Result |
|---|---:|
| Days evaluated | 1,857 |
| Total anomalies | 52 |
| Unusually high days | 26 |
| Unusually low days | 26 |

This approach helps distinguish unusual sales activity from normal weekday variations.

---

## 8. Machine Learning — Isolation Forest

Implemented an unsupervised machine learning approach using the Isolation Forest algorithm.

The model identifies unusual sales behaviour across the 10 retail stores.

### Feature Engineering

Three historical features were developed:

1. **Daily Sales Deviation:** Difference between actual sales and the previous 7-day average.
2. **Weekday Deviation:** Difference between actual sales and the historical average for the same weekday.
3. **Sales Trend:** Comparison between the previous 7-day and 28-day average sales.

All rolling averages use historical observations rather than the current day's sales.

### Model Configuration

| Parameter | Configuration |
|---|---|
| Algorithm | Isolation Forest |
| Estimators | 200 |
| Random State | 42 |
| Contamination | Auto |
| Training Strategy | Chronological 80/20 split |

### Training and Testing

| Parameter | Result |
|---|---|
| Training records | 14,800 |
| Testing records | 3,710 |
| Training period | April 2011 – April 2015 |
| Testing period | April 2015 – April 2016 |

The chronological split ensures the model is evaluated on later historical observations rather than randomly mixed records.

---

## 9. Model Evaluation

Two Isolation Forest approaches were compared using the same 3,710 test records.

### Model Comparison

| Metric | Original Model | Weekday-Adjusted Model |
|---|---:|---:|
| Anomalies detected | 473 | 374 |
| Both models flagged | 284 | 284 |
| Original-only detections | 189 | — |
| Adjusted-only detections | — | 90 |
| Rule-based alerts | 98 | 98 |
| Rule-alert coverage | 93.88% | 74.49% |

### Weekday-Adjusted Model Results

| Metric | Result |
|---|---:|
| Test records | 3,710 |
| ML anomalies detected | 374 |
| ML anomaly rate | 10.08% |
| Rule-based alerts | 98 |
| Both methods flagged | 73 |
| ML-only detections | 301 |
| Rule-only detections | 25 |
| Rule-alert coverage | 74.49% |

### Key Observation

The weekday-adjusted model reduced weekend anomaly concentration.

For example:

| Weekday | Original Model | Adjusted Model |
|---|---:|---:|
| Saturday | 21.70% | 12.26% |
| Sunday | 20.00% | 11.70% |

These results suggest that weekday-adjusted features change the distribution of detected anomalies.

The weekday-adjusted model was selected as the primary experimental model.

**Important:** Rule-based alerts are comparison references, not verified ground-truth labels. Rule-alert coverage must not be interpreted as model accuracy.

---

## 10. Power BI Dashboard

Developed an interactive Power BI dashboard to monitor historical sales performance and investigate detected anomalies.

### Dashboard Components

**Business Performance KPIs**
- Total Units Sold
- Average Daily Sales
- Anomaly Days
- Store Decline Alerts
- Widespread Alert Days

**Sales Analysis**
- Daily Sales Trend
- Monthly Sales Pattern
- High vs Low Anomaly Distribution

**Store Monitoring**
- Store-wise Decline Alerts
- Widespread Store Decline Analysis

**Machine Learning Insights**
- ML-Detected Anomalies
- ML Anomaly Rate
- Weekday-Adjusted ML Anomaly Trend
- Store-wise ML Anomaly Distribution

**Interactive Filters**
- Year
- Month
- Date Range

The dashboard connects historical sales analysis, rule-based monitoring, and machine learning outputs in one reporting environment.

---

## 11. Business Value

SignalSentinel AI demonstrates how historical retail data can be converted into a structured monitoring and investigation workflow.

Potential business applications include:

- Identifying unusual sales activity.
- Prioritizing stores for further investigation.
- Monitoring store-level performance changes.
- Understanding weekday and monthly sales patterns.
- Comparing statistical and machine learning detection approaches.
- Supporting data-driven business decisions through interactive reporting.

The system highlights potential issues; business teams must investigate the underlying causes.

---

## 12. Limitations and Future Improvements

### Current Limitations

- No independently verified anomaly labels are available.
- Model accuracy cannot currently be established.
- Rule-based thresholds require further validation.
- Historical anomaly detection does not establish causation.
- The current system does not produce validated future-sales forecasts or prospective decline-risk predictions.

### Future Improvements

- Develop a validated future sales forecasting model.
- Introduce predictive store-level decline-risk scoring.
- Improve anomaly detection with additional seasonal features.
- Evaluate alternative anomaly detection algorithms.
- Establish a feedback mechanism for verified business anomalies.
- Develop automated monitoring and alert reporting.
- Explore deployment as a production monitoring application.

---

## 13. Project Status

| Component | Status |
|---|---|
| Dataset preparation | Completed |
| PostgreSQL data integration | Completed |
| Exploratory data analysis | Completed |
| Daily, weekly and monthly analysis | Completed |
| Rule-based decline detection | Completed |
| Statistical anomaly detection | Completed |
| Isolation Forest implementation | Completed |
| Chronological model evaluation | Completed |
| Model comparison | Completed |
| Power BI dashboard | Completed |
| ML evaluation documentation | Completed |
| Production deployment | Future improvement |

---

## 14. Key Takeaway

SignalSentinel AI combines SQL, Python, statistical analysis, machine learning, and Power BI to demonstrate an end-to-end retail analytics and historical anomaly monitoring workflow.

It provides a practical example of how data analytics and unsupervised machine learning can support business performance monitoring and investigation.

---

## Author

**Anjeet Yadav**

Data Analytics | SQL | Python | Machine Learning | Power BI

- GitHub: anjeetyadav
- Kaggle: anjeetyadav

---

*This project is an analytical portfolio project based on historical retail sales data. Its anomaly detections are experimental and should not be treated as verified business incidents or production-ready predictions.*
