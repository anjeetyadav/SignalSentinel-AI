<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&pause=1000&color=110B3DDB&width=435&lines=SignalSentinel+AI" alt="Typing SVG" /></a># SignalSentinel AI
### Intelligent Business Early-Warning System

## Overview

SignalSentinel AI is a portfolio project designed to investigate historical product sales patterns and develop an evidence-based early-warning system for potential sales deterioration.

The project combines data analytics, statistical analysis, anomaly detection, predictive modeling, SQL, and interactive Power BI reporting.

## Business Problem

Businesses need ways to identify unusual sales patterns and recognize products that may require further investigation.

This project will explore whether historical sales, calendar information, and product pricing can help identify unusual behavior and predict future sales declines.

The prediction target and evaluation methodology will be defined after examining the dataset.

## Dataset

Planned dataset: M5 Forecasting Accuracy, available through Kaggle.

The dataset contains historical Walmart sales, calendar information, and product pricing data.

Dataset source: https://www.kaggle.com/competitions/m5-forecasting-accuracy

## Planned Technology Stack

- Python
- Pandas and NumPy
- SQL / PostgreSQL
- Exploratory Data Analysis
- Statistical analysis
- Scikit-learn
- Isolation Forest
- Classification models
- Power BI, DAX, and Power Query
- Git and GitHub

## Project Progress

### Completed

* [x] Defined project objective and business problem.
* [x] Created GitHub repository and project structure.
* [x] Downloaded and inspected the M5 dataset.
* [x] Performed initial data quality checks.
* [x] Analyzed daily, weekly, monthly and yearly sales patterns.
* [x] Investigated year-end sales patterns.
* [x] Developed rule-based store decline detection.
* [x] Investigated December 2014 store alerts.
* [x] Investigated store calendar effects and widespread alerts.
* [x] Implemented weekday-adjusted anomaly detection.
* [x] Identified 52 unusual sales days: 26 unusually high and 26 unusually low.
* [x] Imported monitoring datasets into Power BI.
* [x] Created a Date table and established date relationships.
* [x] Created daily sales, anomaly, store decline and widespread alert KPI measures.

### In Progress

* [ ] Build the Power BI executive overview.
* [ ] Create anomaly and store monitoring visuals.
* [ ] Validate the complete Power BI data model.
* [ ] Consolidate findings into business recommendations.

### Remaining

* [ ] Review and finalize detection methodology.
* [ ] Complete appropriate model evaluation.
* [ ] Document limitations and findings.
* [ ] Capture dashboard screenshots.
* [ ] Finalize GitHub documentation.

### Current Status

The project has completed its initial exploratory analysis and rule-based anomaly detection stages. Existing analytical outputs have been imported into Power BI, and the initial KPI measures have been created.

The executive dashboard is currently under development.

### Important Limitation

Detected anomalies and potential sales declines are investigation signals, not proof of business problems or their causes. The detection thresholds and methodology require appropriate validation before operational use.
 be based on verified analytical results.
