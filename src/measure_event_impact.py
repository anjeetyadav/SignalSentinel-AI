import pandas as pd

# ---------- Load ----------
sales = pd.read_csv("reports/daily_sales_totals.csv", parse_dates=["date"])
cal = pd.read_csv(
    "data/raw/calendar.csv",
    usecols=["date", "event_name_1", "event_name_2"],
    parse_dates=["date"],
)

df = sales.merge(cal, on="date", how="left").sort_values("date").set_index("date")
df["has_event"] = df["event_name_1"].notna() | df["event_name_2"].notna()

units = df["total_units_sold"]
is_event = df["has_event"]

# ---------- Ratio for each event day ----------
rows = []
for date in df.index[df["event_name_1"].notna()]:
    # same weekday, 4 weeks before and 4 weeks after
    neighbours = [date + pd.Timedelta(weeks=k) for k in range(-4, 5) if k != 0]
    neighbours = [d for d in neighbours if d in df.index and not is_event[d]]
    if len(neighbours) < 4:
        continue  # not enough clean comparison days
    baseline = units[neighbours].mean()
    rows.append({
        "event_name": df.loc[date, "event_name_1"],
        "event_type": cal.loc[cal["date"] == date, "event_name_1"].iloc[0] and
                      pd.read_csv("data/raw/calendar.csv", usecols=["date", "event_type_1"],
                                  parse_dates=["date"]).set_index("date").loc[date, "event_type_1"],
        "date": date,
        "units": units[date],
        "baseline_same_weekday": round(baseline, 1),
        "ratio": units[date] / baseline,
    })

events = pd.DataFrame(rows)

# ---------- Summarise by event ----------
summary = (
    events.groupby("event_name")
    .agg(
        event_type=("event_type", "first"),
        occurrences=("ratio", "count"),
        avg_ratio=("ratio", "mean"),
        min_ratio=("ratio", "min"),
        max_ratio=("ratio", "max"),
    )
    .round(3)
    .sort_values("avg_ratio")
)

print(f"Events measured: {len(events)} occurrences across {len(summary)} named events")
print("\n=== EVENT IMPACT (ratio = event-day sales / same-weekday baseline) ===")
print(summary.to_string())

summary.to_csv("reports/event_impact_summary.csv")
events.to_csv("reports/event_impact_detail.csv", index=False)
print("\nSaved: reports/event_impact_summary.csv and reports/event_impact_detail.csv")