import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import IsolationForest


# 1. PROJECT PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "reports" / "store_decline_analysis.csv"
OUTPUT_FILE = BASE_DIR / "reports" / "ml_anomaly_weekday_adjusted_test.csv"
SUMMARY_FILE = BASE_DIR / "reports" / "ml_anomaly_weekday_summary.csv"
MODEL_FILE = BASE_DIR / "models" / "isolation_forest_weekday_adjusted.pkl"


# 2. LOAD DATA

df = pd.read_csv(INPUT_FILE)
df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(["store_id", "date"]).reset_index(drop=True)

print("Dataset loaded:", df.shape)


# 3. FEATURE ENGINEERING

df["weekday"] = df["date"].dt.dayofweek

# Previous 7 days, excluding current day
df["past_7d_avg"] = (
    df.groupby("store_id")["units_sold"]
    .transform(lambda s: s.shift(1).rolling(7).mean())
)

# Previous 28 days, excluding current day
df["past_28d_avg"] = (
    df.groupby("store_id")["units_sold"]
    .transform(lambda s: s.shift(1).rolling(28).mean())
)

# Previous 8 observations for the same weekday
df["same_weekday_avg"] = (
    df.groupby(["store_id", "weekday"])["units_sold"]
    .transform(lambda s: s.shift(1).rolling(8, min_periods=4).mean())
)

# Today's sales compared with previous 7-day average
df["daily_deviation_pct"] = (
    (df["units_sold"] - df["past_7d_avg"])
    / df["past_7d_avg"].replace(0, np.nan)
) * 100

# Today's sales compared with historical same-weekday average
df["weekday_deviation_pct"] = (
    (df["units_sold"] - df["same_weekday_avg"])
    / df["same_weekday_avg"].replace(0, np.nan)
) * 100

# Previous 7-day trend compared with previous 28-day trend
df["sales_trend_pct"] = (
    (df["past_7d_avg"] - df["past_28d_avg"])
    / df["past_28d_avg"].replace(0, np.nan)
) * 100


# 4. SELECT FEATURES

features = [
    "daily_deviation_pct",
    "weekday_deviation_pct",
    "sales_trend_pct"
]

df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna(subset=features).copy()

print("\nValid records after feature engineering:", len(df))


# 5. CHRONOLOGICAL 80/20 SPLIT

unique_dates = sorted(df["date"].unique())

split_index = int(len(unique_dates) * 0.80)
split_date = unique_dates[split_index]

train = df[df["date"] < split_date].copy()
test = df[df["date"] >= split_date].copy()

X_train = train[features]
X_test = test[features]

print("\nTraining period:")
print(train["date"].min(), "to", train["date"].max())
print("Training records:", len(train))

print("\nTesting period:")
print(test["date"].min(), "to", test["date"].max())
print("Testing records:", len(test))


# 6. TRAIN ISOLATION FOREST

model = IsolationForest(
    n_estimators=200,
    contamination="auto",
    random_state=42
)

model.fit(X_train)

print("\nWeekday-adjusted model trained.")


# 7. DETECT TEST ANOMALIES

test["ml_prediction"] = model.predict(X_test)

test["ml_anomaly"] = test["ml_prediction"] == -1

test["anomaly_score"] = model.decision_function(X_test)


# 8. COMPARE WITH RULE-BASED DETECTOR

test["rule_based_alert"] = test["potential_decline_alert"]

test["both_methods_flagged"] = (
    test["ml_anomaly"] & test["rule_based_alert"]
)

test["ml_only_flagged"] = (
    test["ml_anomaly"] & ~test["rule_based_alert"]
)

test["rule_only_flagged"] = (
    ~test["ml_anomaly"] & test["rule_based_alert"]
)


# 9. SAVE RESULTS

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)

test.to_csv(OUTPUT_FILE, index=False)

joblib.dump(model, MODEL_FILE)

print("\nTest results saved:", OUTPUT_FILE)
print("Model saved:", MODEL_FILE)


# 10. STORE-WISE SUMMARY

summary = test.groupby("store_id").agg(
    total_records=("store_id", "size"),
    ml_anomalies=("ml_anomaly", "sum"),
    rule_based_alerts=("rule_based_alert", "sum"),
    both_flagged=("both_methods_flagged", "sum"),
    ml_only=("ml_only_flagged", "sum"),
    rule_only=("rule_only_flagged", "sum")
).reset_index()

summary.to_csv(SUMMARY_FILE, index=False)


# 11. RESULTS

total = len(test)
ml_count = int(test["ml_anomaly"].sum())
rule_count = int(test["rule_based_alert"].sum())
both_count = int(test["both_methods_flagged"].sum())

print("\n========== WEEKDAY-ADJUSTED ML RESULTS ==========")

print("Training records:", len(train))
print("Testing records:", total)
print("ML anomalies:", ml_count)
print("Rule-based alerts:", rule_count)
print("Both flagged:", both_count)
print("ML-only:", int(test["ml_only_flagged"].sum()))
print("Rule-only:", int(test["rule_only_flagged"].sum()))

if rule_count:
    print(
        "Rule alert coverage:",
        round(both_count / rule_count * 100, 2), "%"
    )

print("\nSTORE-WISE SUMMARY")
print(summary.to_string(index=False))

print("\nWeekday-adjusted anomaly detection completed.")