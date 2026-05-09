"""
metrics.py — Calculates business metrics from sales data.
Reads sales_data.csv and produces structured metrics for AI summarization.
"""

import pandas as pd
from pathlib import Path

# Path to the CSV — resolves relative to this script's location
DATA_FILE = Path(__file__).parent / "sales_data.csv"


def load_sales_data() -> pd.DataFrame:
    """
    Load sales data from CSV and parse dates properly.
    Returns a pandas DataFrame.
    Raises FileNotFoundError if the file is missing.
    """
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Sales data file not found: {DATA_FILE}\n"
            "Run `python generate_sample_data.py` first to create it."
        )

    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    return df


def inspect_data(df: pd.DataFrame) -> None:
    """Print a quick summary so we can verify the load worked."""
    print("=" * 60)
    print("SALES DATA SUMMARY")
    print("=" * 60)
    print(f"Total rows:    {len(df):,}")
    print(f"Date range:    {df['date'].min().date()}  →  {df['date'].max().date()}")
    print(f"Columns:       {list(df.columns)}")
    print(f"Total revenue: ₹{df['revenue'].sum():,.0f}")
    print(f"Unique SKUs:   {df['sku'].nunique()}")
    print(f"Channels:      {df['channel'].unique().tolist()}")
    print("=" * 60)

def get_daily_snapshot(df: pd.DataFrame) -> dict:
    """
    Compare the latest day in the data vs the day before.
    Returns a dict with revenue, orders, AOV, and % changes.
    """
    # Get unique dates, sorted
    dates = sorted(df["date"].dt.date.unique())

    if len(dates) < 2:
        raise ValueError("Need at least 2 days of data for comparison")

    today = dates[-1]
    yesterday = dates[-2]

    today_df = df[df["date"].dt.date == today]
    yesterday_df = df[df["date"].dt.date == yesterday]

    today_revenue = today_df["revenue"].sum()
    yesterday_revenue = yesterday_df["revenue"].sum()
    today_orders = len(today_df)
    yesterday_orders = len(yesterday_df)

    today_aov = today_revenue / today_orders if today_orders else 0
    yesterday_aov = yesterday_revenue / yesterday_orders if yesterday_orders else 0

    def pct_change(current, previous):
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100

    return {
        "date": today.isoformat(),
        "comparison_date": yesterday.isoformat(),
        "revenue": float(today_revenue),
        "revenue_prev": float(yesterday_revenue),
        "revenue_change_pct": round(pct_change(today_revenue, yesterday_revenue), 2),
        "orders": int(today_orders),
        "orders_prev": int(yesterday_orders),
        "orders_change_pct": round(pct_change(today_orders, yesterday_orders), 2),
        "aov": round(today_aov, 2),
        "aov_prev": round(yesterday_aov, 2),
        "aov_change_pct": round(pct_change(today_aov, yesterday_aov), 2),
    }


def print_daily_snapshot(snapshot: dict) -> None:
    """Pretty-print the daily snapshot for terminal viewing."""
    arrow = lambda pct: "▲" if pct > 0 else ("▼" if pct < 0 else "▬")

    print("\n" + "=" * 60)
    print(f"DAILY SNAPSHOT — {snapshot['date']}")
    print(f"(vs {snapshot['comparison_date']})")
    print("=" * 60)
    print(f"Revenue:    ₹{snapshot['revenue']:>12,.0f}   "
          f"{arrow(snapshot['revenue_change_pct'])} {snapshot['revenue_change_pct']:+.1f}%")
    print(f"Orders:     {snapshot['orders']:>13,}   "
          f"{arrow(snapshot['orders_change_pct'])} {snapshot['orders_change_pct']:+.1f}%")
    print(f"Avg Order:  ₹{snapshot['aov']:>12,.0f}   "
          f"{arrow(snapshot['aov_change_pct'])} {snapshot['aov_change_pct']:+.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    df = load_sales_data()
    inspect_data(df)

    snapshot = get_daily_snapshot(df)
    print_daily_snapshot(snapshot)