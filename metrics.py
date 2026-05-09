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

def get_weekly_comparison(df: pd.DataFrame) -> dict:
    """
    Compare the last 7 days vs the 7 days before that.
    Returns a dict with revenue, orders, AOV, and % changes.
    """
    latest_date = df["date"].max().date()

    # Last 7 days: latest_date down to (latest_date - 6)
    last_7_start = latest_date - pd.Timedelta(days=6)
    last_7_end = latest_date

    # Previous 7 days: (latest_date - 13) down to (latest_date - 7)
    prev_7_start = latest_date - pd.Timedelta(days=13)
    prev_7_end = latest_date - pd.Timedelta(days=7)

    last_7_df = df[
        (df["date"].dt.date >= last_7_start) & (df["date"].dt.date <= last_7_end)
    ]
    prev_7_df = df[
        (df["date"].dt.date >= prev_7_start) & (df["date"].dt.date <= prev_7_end)
    ]

    last_revenue = last_7_df["revenue"].sum()
    prev_revenue = prev_7_df["revenue"].sum()
    last_orders = len(last_7_df)
    prev_orders = len(prev_7_df)

    last_aov = last_revenue / last_orders if last_orders else 0
    prev_aov = prev_revenue / prev_orders if prev_orders else 0

    def pct_change(current, previous):
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100

    return {
        "last_7_start": last_7_start.isoformat(),
        "last_7_end": last_7_end.isoformat(),
        "prev_7_start": prev_7_start.isoformat(),
        "prev_7_end": prev_7_end.isoformat(),
        "revenue": float(last_revenue),
        "revenue_prev": float(prev_revenue),
        "revenue_change_pct": round(pct_change(last_revenue, prev_revenue), 2),
        "orders": int(last_orders),
        "orders_prev": int(prev_orders),
        "orders_change_pct": round(pct_change(last_orders, prev_orders), 2),
        "aov": round(last_aov, 2),
        "aov_prev": round(prev_aov, 2),
        "aov_change_pct": round(pct_change(last_aov, prev_aov), 2),
    }

def print_weekly_comparison(weekly: dict) -> None:
    """Pretty-print the weekly comparison."""
    arrow = lambda pct: "▲" if pct > 0 else ("▼" if pct < 0 else "▬")

    print("\n" + "=" * 60)
    print(f"LAST 7 DAYS  ({weekly['last_7_start']} → {weekly['last_7_end']})")
    print(f"vs PREV 7    ({weekly['prev_7_start']} → {weekly['prev_7_end']})")
    print("=" * 60)
    print(f"Revenue:    ₹{weekly['revenue']:>12,.0f}   "
          f"vs ₹{weekly['revenue_prev']:>10,.0f}   "
          f"{arrow(weekly['revenue_change_pct'])} {weekly['revenue_change_pct']:+.1f}%")
    print(f"Orders:     {weekly['orders']:>13,}   "
          f"vs {weekly['orders_prev']:>11,}   "
          f"{arrow(weekly['orders_change_pct'])} {weekly['orders_change_pct']:+.1f}%")
    print(f"Avg Order:  ₹{weekly['aov']:>12,.0f}   "
          f"vs ₹{weekly['aov_prev']:>10,.0f}   "
          f"{arrow(weekly['aov_change_pct'])} {weekly['aov_change_pct']:+.1f}%")
    print("=" * 60)

def get_top_performers(df: pd.DataFrame, days: int = 7) -> dict:
    """
    Find top products, channel, and city for the last N days (default 7).
    Returns a dict with structured data for AI summarization.
    """
    latest_date = df["date"].max().date()
    start_date = latest_date - pd.Timedelta(days=days - 1)

    window_df = df[
        (df["date"].dt.date >= start_date) & (df["date"].dt.date <= latest_date)
    ].copy()

    total_revenue = window_df["revenue"].sum()

    # Top 3 products by revenue
    product_stats = (
        window_df.groupby(["sku", "product_name"])
        .agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(3)
    )

    top_products = [
        {
            "sku": row["sku"],
            "name": row["product_name"],
            "revenue": float(row["revenue"]),
            "units": int(row["units"]),
            "share_pct": round((row["revenue"] / total_revenue) * 100, 2),
        }
        for _, row in product_stats.iterrows()
    ]

    # Channel breakdown
    channel_stats = (
        window_df.groupby("channel")
        .agg(revenue=("revenue", "sum"), orders=("order_id", "count"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    channels = [
        {
            "channel": row["channel"],
            "revenue": float(row["revenue"]),
            "orders": int(row["orders"]),
            "share_pct": round((row["revenue"] / total_revenue) * 100, 2),
        }
        for _, row in channel_stats.iterrows()
    ]

    # Top 3 cities
    city_stats = (
        window_df.groupby("city")
        .agg(revenue=("revenue", "sum"), orders=("order_id", "count"))
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(3)
    )

    top_cities = [
        {
            "city": row["city"],
            "revenue": float(row["revenue"]),
            "orders": int(row["orders"]),
            "share_pct": round((row["revenue"] / total_revenue) * 100, 2),
        }
        for _, row in city_stats.iterrows()
    ]

    return {
        "window_start": start_date.isoformat(),
        "window_end": latest_date.isoformat(),
        "total_revenue": float(total_revenue),
        "top_products": top_products,
        "channels": channels,
        "top_cities": top_cities,
    }

def print_top_performers(performers: dict) -> None:
    """Pretty-print the top performers section."""
    print("\n" + "=" * 60)
    print(f"TOP PERFORMERS — Last 7 Days "
          f"({performers['window_start']} → {performers['window_end']})")
    print("=" * 60)

    print("\nTop Products:")
    for i, p in enumerate(performers["top_products"], 1):
        print(f"  {i}. {p['name']:<22} ₹{p['revenue']:>10,.0f}  "
              f"({p['units']} units, {p['share_pct']:.1f}% of revenue)")

    print("\nChannel Breakdown:")
    for c in performers["channels"]:
        print(f"  {c['channel']:<14} ₹{c['revenue']:>10,.0f}  "
              f"({c['orders']} orders, {c['share_pct']:.1f}% of revenue)")

    print("\nTop Cities:")
    for i, ct in enumerate(performers["top_cities"], 1):
        print(f"  {i}. {ct['city']:<14} ₹{ct['revenue']:>10,.0f}  "
              f"({ct['orders']} orders, {ct['share_pct']:.1f}% of revenue)")
    print("=" * 60)

if __name__ == "__main__":
    df = load_sales_data()
    inspect_data(df)

    snapshot = get_daily_snapshot(df)
    print_daily_snapshot(snapshot)

    weekly = get_weekly_comparison(df)
    print_weekly_comparison(weekly)

    performers = get_top_performers(df)
    print_top_performers(performers)