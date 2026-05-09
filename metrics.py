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


if __name__ == "__main__":
    df = load_sales_data()
    inspect_data(df)