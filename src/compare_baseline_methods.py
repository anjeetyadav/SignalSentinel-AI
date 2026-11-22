import numpy as np
import pandas as pd

THRESHOLD = -15.0      # alert if change is 15% or more below baseline
WIDESPREAD_MIN = 5     # "widespread" = at least 5 stores flagged on one date

METHODS = {
    "A": "Original 7d vs 28d",
    "B": "Calendar-aware (Christmas excluded)",
    "C": "Weekday-adjusted",
    "D": "Weekday-adjusted + Christmas excluded",
}

# ---------- Load data ----------
stores = pd.read_csv(
    "reports/store_decline_analysis.csv",
    usecols=["store_id", "date", "units_sold", "potential_decline_alert"],
    parse_dates=["date"],
)
calendar = pd.read_csv(
    "data/raw/calendar.csv",
    usecols=["date", "event_name_1", "event_name_2"],
    parse_dates=["date"],
)
calendar["is_christmas"] = (
    (calendar["event_name_1"] == "Christmas")
    | (calendar["event_name_2"] == "Christmas")
)

df = stores.merge(calendar[["date", "is_christmas"]], on="date", how="left")
df = df.sort_values(["store_id", "date"]).reset_index(drop=True)
df["weekday"] = df["date"].dt.dayofweek

# Same sales, but Christmas Day becomes "missing" so it is ignored in averages
df["units_masked"] = df["units_sold"].where(~df["is_christmas"])


# ---------- Detector methods (per store) ----------
def add_methods(g):
    g = g.copy()

    # A: original rule
    recent = g["units_sold"].rolling(7).mean()
    previous = g["units_sold"].rolling(28).mean().shift(7)
    g["chg_A"] = (recent / previous - 1) * 100

    # B: same rule, Christmas excluded from both windows
    recent_m = g["units_masked"].rolling(7, min_periods=5).mean()
    previous_m = g["units_masked"].rolling(28, min_periods=24).mean().shift(7)
    g["chg_B"] = (recent_m / previous_m - 1) * 100

    # C and D: weekday-adjusted
    for tag, col in [("C", "units_sold"), ("D", "units_masked")]:
        expected = g.groupby("weekday")[col].transform(
            lambda s: s.shift(1).rolling(8, min_periods=6).mean()
        )
        ratio = (g[col] / expected).replace([np.inf, -np.inf], np.nan)
        g[f"chg_{tag}"] = (ratio.rolling(7, min_periods=5).mean() - 1) * 100

    return g


df = pd.concat([add_methods(g) for _, g in df.groupby("store_id")], ignore_index=True)

# ---------- Common window: only rows where all four methods exist ----------
chg_cols = [f"chg_{m}" for m in METHODS]
common = df.dropna(subset=chg_cols).copy()
for m in METHODS:
    common[f"alert_{m}"] = common[f"chg_{m}"] <= THRESHOLD

print(f"Common window: {common['date'].min().date()} to {common['date'].max().date()}")
print(f"Store-days compared: {len(common):,} "
      f"({common['store_id'].nunique()} stores, {common['date'].nunique()} dates)")

# ---------- Sanity check: does rebuilt A match the stored original alert? ----------
a_rows = df.dropna(subset=["chg_A"])
rebuilt = a_rows["chg_A"] <= THRESHOLD
mismatch = (rebuilt != a_rows["potential_decline_alert"]).sum()
print(f"\nSanity check: rebuilt method A vs stored alert -> "
      f"{mismatch} mismatches out of {len(a_rows):,} rows")

# ---------- Daily count of stores flagged, per method ----------
daily = common.groupby("date")[[f"alert_{m}" for m in METHODS]].sum()
daily.columns = list(METHODS)

# ---------- Summary table ----------
rows = []
for m, name in METHODS.items():
    flagged = common[f"alert_{m}"]
    widespread = daily[m] >= WIDESPREAD_MIN
    wide_dates = daily.index[widespread]
    dec_wide = (wide_dates.month == 12).sum()
    xmas_window = common["date"].dt.month.eq(12) & common["date"].dt.day.between(25, 31)
    yearly_rate = flagged.groupby(common["date"].dt.year).mean() * 100

    rows.append({
        "method": m,
        "description": name,
        "alert_store_days": int(flagged.sum()),
        "alert_rate_pct": round(flagged.mean() * 100, 2),
        "dates_with_any_alert": int((daily[m] >= 1).sum()),
        "widespread_dates_ge5": int(widespread.sum()),
        "all_10_stores_dates": int((daily[m] == 10).sum()),
        "widespread_in_december": int(dec_wide),
        "alerts_dec25_to_31": int(flagged[xmas_window].sum()),
        "yearly_rate_std": round(yearly_rate.std(), 2),
    })

summary = pd.DataFrame(rows)
print("\n=== METHOD COMPARISON ===")
print(summary.to_string(index=False))

# ---------- Alerts per store ----------
store_alerts = pd.DataFrame(
    {m: common.groupby("store_id")[f"alert_{m}"].sum() for m in METHODS}
)
print("\n=== ALERT DAYS PER STORE ===")
print(store_alerts.to_string())

# ---------- Alert rate by year (stability) ----------
yearly = pd.DataFrame(
    {m: common.groupby(common["date"].dt.year)[f"alert_{m}"].mean() * 100
     for m in METHODS}
).round(2)
yearly.index.name = "year"
print("\n=== ALERT RATE (%) BY YEAR ===")
print(yearly.to_string())

# ---------- Stores flagged on the Dec 2014 dates we investigated ----------
print("\n=== STORES FLAGGED, DEC 2014 (out of 10) ===")
dec14 = daily.loc["2014-12-26":"2014-12-31"]
print(dec14.to_string())

# ---------- Save ----------
summary.to_csv("reports/baseline_method_comparison.csv", index=False)
store_alerts.to_csv("reports/baseline_method_store_alerts.csv")
yearly.to_csv("reports/baseline_method_yearly_alert_rates.csv")
daily.to_csv("reports/baseline_method_daily_store_counts.csv")
print("\nSaved 4 files to reports/ (prefix: baseline_method_)")