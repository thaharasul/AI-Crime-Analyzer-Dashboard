

import pandas as pd

from config import CRIME_CSV_PATH


def _load_df() -> pd.DataFrame:
    df = pd.read_csv(CRIME_CSV_PATH, parse_dates=["date_reported"])
    return df


def top_categories(df: pd.DataFrame, n=5):
    counts = df["category"].value_counts().head(n)
    return [{"category": k, "count": int(v)} for k, v in counts.items()]


def busiest_zones(df: pd.DataFrame, n=5):
    counts = df["zone"].value_counts().head(n)
    return [{"zone": k, "count": int(v)} for k, v in counts.items()]


def peak_hours(df: pd.DataFrame, n=5):
    counts = df["hour_of_day"].value_counts().sort_values(ascending=False).head(n)
    return [{"hour": int(k), "count": int(v)} for k, v in counts.items()]


def detect_zone_anomalies(df: pd.DataFrame, recent_days=14, baseline_days=90):
    
    
    max_date = df["date_reported"].max()
    recent_cutoff = max_date - pd.Timedelta(days=recent_days)
    baseline_cutoff = max_date - pd.Timedelta(days=baseline_days)

    recent = df[df["date_reported"] >= recent_cutoff]
    baseline = df[(df["date_reported"] >= baseline_cutoff) & (df["date_reported"] < recent_cutoff)]

    recent_rate = recent.groupby("zone").size() / max(recent_days, 1)
    baseline_rate = baseline.groupby("zone").size() / max(baseline_days - recent_days, 1)

    anomalies = []
    for zone in recent_rate.index:
        base = baseline_rate.get(zone, 0)
        cur = recent_rate[zone]
        if base > 0 and cur >= base * 1.4:
            anomalies.append({
                "zone": zone,
                "recent_daily_rate": round(float(cur), 2),
                "baseline_daily_rate": round(float(base), 2),
                "increase_pct": round(((cur - base) / base) * 100, 1),
            })
    return sorted(anomalies, key=lambda a: a["increase_pct"], reverse=True)


def run_full_analysis() -> dict:
    df = _load_df()
    return {
        "total_crimes": int(len(df)),
        "top_categories": top_categories(df),
        "busiest_zones": busiest_zones(df),
        "peak_hours": peak_hours(df),
        "zone_anomalies": detect_zone_anomalies(df),
    }
