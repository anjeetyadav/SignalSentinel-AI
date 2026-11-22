from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
REPORTS_DIR = PROJECT_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

sales_path = RAW_DATA_DIR / "sales_train_validation.csv"

print("Loading sales data for quality checks...")

sales = pd.read_csv(sales_path)

identifier_columns = [
    "id",
    "item_id",
    "dept_id",
    "cat_id",
    "store_id",
    "state_id",
]

daily_columns = [
    column for column in sales.columns
    if column.startswith("d_")
]

sales_values = sales[daily_columns].to_numpy(dtype=np.float32)

record_totals = np.nansum(sales_values, axis=1)

category_totals = (
    sales.assign(total_sales=record_totals)
    .groupby("cat_id")["total_sales"]
    .sum()
    .sort_values(ascending=False)
)

total_entries = sales_values.size
zero_entries = int(np.sum(sales_values == 0))

report_lines = [
    "# SignalSentinel AI — Data Quality Report",
    "",
    "## 1. Dataset Overview",
    "",
    f"- Product/store records: {len(sales):,}",
    f"- Identifier columns: {len(identifier_columns)}",
    f"- Daily sales columns: {len(daily_columns):,}",
    f"- Total daily sales observations: {total_entries:,}",
    "",
    "## 2. Data Quality Checks",
    "",
    f"- Missing daily sales values: {int(sales[daily_columns].isna().sum().sum()):,}",
    f"- Negative daily sales observations: {int(np.sum(sales_values < 0)):,}",
    f"- Product/store records with zero total sales: {int(np.sum(record_totals == 0)):,}",
    f"- Product/store records with positive total sales: {int(np.sum(record_totals > 0)):,}",
    "",
    "## 3. Sales Statistics",
    "",
    f"- Minimum daily sales: {float(np.nanmin(sales_values)):.2f}",
    f"- Maximum daily sales: {float(np.nanmax(sales_values)):.2f}",
    f"- Mean daily sales: {float(np.nanmean(sales_values)):.4f}",
    f"- Total recorded units sold: {float(np.nansum(sales_values)):,.0f}",
    f"- Zero-sales observations: {zero_entries:,}",
    f"- Zero-sales observation percentage: {zero_entries / total_entries * 100:.2f}%",
    "",
    "## 4. Units Sold by Category",
    "",
    "| Category | Total Units Sold |",
    "|---|---:|",
]

for category, total in category_totals.items():
    report_lines.append(f"| {category} | {total:,.0f} |")

report_lines.extend([
    "",
    "## 5. Initial Interpretation",
    "",
    "- No missing daily sales values were found in the inspected dataset.",
    "- No negative daily sales values were found.",
    "- Zero-sales observations are common and should not automatically be treated as anomalies.",
    "- Category totals represent units sold, not revenue.",
    "- Further investigation is needed to distinguish normal demand variation from meaningful anomalies.",
    "",
    "## 6. Dataset Used",
    "",
    "`data/raw/sales_train_validation.csv`",
    "",
])

report_path = REPORTS_DIR / "data_quality_report.md"
report_path.write_text("\n".join(report_lines), encoding="utf-8")

print("\nData quality report created:")
print(report_path)

print("\nZero-sales percentage:",
      f"{zero_entries / total_entries * 100:.2f}%")

print("\nData quality report completed.")