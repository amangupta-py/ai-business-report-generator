"""
main.py — Daily Business Report Generator
Orchestrates the full pipeline: load data → compute metrics → AI summary → email.

Usage:
    python main.py

Configuration:
    Edit RECIPIENTS below, or set REPORT_RECIPIENTS in .env (comma-separated).
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from metrics import (
    load_sales_data,
    get_daily_snapshot,
    get_weekly_comparison,
    get_top_performers,
)
from ai_summarizer import generate_summary
from email_sender import send_report_email, build_subject

load_dotenv()

# === Configuration ===
# Comma-separated list of email addresses, set in .env file
# Example in .env:  REPORT_RECIPIENTS=alice@company.com,bob@company.com
RECIPIENTS_ENV = os.getenv("REPORT_RECIPIENTS", "")
RECIPIENTS = [email.strip() for email in RECIPIENTS_ENV.split(",") if email.strip()]


def run_pipeline(send_email: bool = True) -> dict:
    """
    Execute the full report generation pipeline.

    Args:
        send_email: If True, sends the report via email. If False, only prints.

    Returns:
        A dict containing the metrics, summary, and delivery status.
    """
    print("=" * 60)
    print(f"Daily Business Report Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/4] Loading sales data...")
    df = load_sales_data()
    print(f"      ✓ Loaded {len(df):,} rows")

    # Step 2: Compute metrics
    print("\n[2/4] Computing metrics...")
    daily = get_daily_snapshot(df)
    weekly = get_weekly_comparison(df)
    performers = get_top_performers(df)
    print(f"      ✓ Daily, weekly, and performer metrics ready")

    # Step 3: Generate AI summary
    print("\n[3/4] Generating AI summary...")
    summary = generate_summary(daily, weekly, performers)
    print(f"      ✓ Summary generated ({len(summary)} chars)")

    # Step 4: Deliver
    print("\n[4/4] Delivering report...")
    delivery_status = "skipped"

    if send_email:
        if not RECIPIENTS:
            print("      ⚠ No recipients configured. Set REPORT_RECIPIENTS in .env")
            print("      Printing report to terminal instead.\n")
            print(summary)
            delivery_status = "no_recipients"
        else:
            subject = build_subject(daily["date"])
            send_report_email(
                recipients=RECIPIENTS,
                subject=subject,
                body=summary,
            )
            print(f"      ✓ Email sent to {len(RECIPIENTS)} recipient(s)")
            delivery_status = "sent"
    else:
        print("      → Email skipped (send_email=False)\n")
        print(summary)
        delivery_status = "printed"

    print("\n" + "=" * 60)
    print("Pipeline complete.")
    print("=" * 60)

    return {
        "report_date": daily["date"],
        "summary": summary,
        "summary_length": len(summary),
        "recipients": RECIPIENTS,
        "delivery_status": delivery_status,
    }


if __name__ == "__main__":
    # Allow optional --no-email flag for testing without sending
    send_email = "--no-email" not in sys.argv

    try:
        result = run_pipeline(send_email=send_email)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)