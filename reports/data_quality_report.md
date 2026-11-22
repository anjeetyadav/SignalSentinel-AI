# SignalSentinel AI — Data Quality Report

## 1. Dataset Overview

- Product/store records: 30,490
- Identifier columns: 6
- Daily sales columns: 1,913
- Total daily sales observations: 58,327,370

## 2. Data Quality Checks

- Missing daily sales values: 0
- Negative daily sales observations: 0
- Product/store records with zero total sales: 0
- Product/store records with positive total sales: 30,490

## 3. Sales Statistics

- Minimum daily sales: 0.00
- Maximum daily sales: 763.00
- Mean daily sales: 1.1263
- Total recorded units sold: 65,695,408
- Zero-sales observations: 39,777,094
- Zero-sales observation percentage: 68.20%

## 4. Units Sold by Category

| Category | Total Units Sold |
|---|---:|
| FOODS | 45,089,940 |
| HOUSEHOLD | 14,480,670 |
| HOBBIES | 6,124,800 |

## 5. Initial Interpretation

- No missing daily sales values were found in the inspected dataset.
- No negative daily sales values were found.
- Zero-sales observations are common and should not automatically be treated as anomalies.
- Category totals represent units sold, not revenue.
- Further investigation is needed to distinguish normal demand variation from meaningful anomalies.

## 6. Dataset Used

`data/raw/sales_train_validation.csv`
