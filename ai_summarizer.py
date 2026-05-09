"""
ai_summarizer.py — Generates AI-written business report from metrics.
Takes structured metrics from metrics.py and produces a readable summary.
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# === Configuration ===
MODEL_NAME = "gemini-2.5-flash"
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found in .env file. "
        "Make sure .env exists in project root."
    )

genai.configure(api_key=API_KEY)


# === Prompt Construction ===
SYSTEM_INSTRUCTIONS = """You are a senior business analyst writing a daily report for an e-commerce founder in India.

Your audience is a busy executive who has 60 seconds to read this. They want:
- The most important numbers up front
- Plain English, no jargon
- Specific insights (not "revenue went up" — explain WHY based on the data)
- Honest tone — flag concerns if numbers look bad
- Actionable suggestions where genuinely useful

Currency: All revenue figures are in Indian Rupees (₹). Always use the ₹ symbol, never $ or USD.

Format the output as a clean business email body. Use short paragraphs. Avoid bullet points unless listing items. No greeting or signature — just the report content.

Length: 200-300 words. Tight. No fluff.
"""


def build_prompt(daily: dict, weekly: dict, performers: dict) -> str:
    """
    Combines structured metrics into a single prompt for the AI.
    Uses JSON formatting so the model can clearly distinguish data sections.
    """
    metrics_json = json.dumps(
        {
            "daily_snapshot": daily,
            "weekly_comparison": weekly,
            "top_performers": performers,
        },
        indent=2,
    )

    prompt = f"""Based on the e-commerce metrics below, write a daily business report.

                METRICS DATA:
                {metrics_json}

                Write the report now. Remember: 200-300 words, executive tone, specific insights, no jargon."""

    return prompt

def generate_summary(daily: dict, weekly: dict, performers: dict) -> str:
    """
    Send metrics to Gemini and return a written business report.
    Raises RuntimeError on API failure with a clear message.
    """
    prompt = build_prompt(daily, weekly, performers)

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTIONS,
        )
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2000,
            },
        )
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {e}") from e

    # Extract text from response, handling both .text shortcut and parts fallback
    text = ""
    if hasattr(response, "text") and response.text:
        text = response.text
    elif hasattr(response, "candidates") and response.candidates:
        parts = response.candidates[0].content.parts
        text = "".join(part.text for part in parts if hasattr(part, "text"))

    if not text:
        raise RuntimeError(
            f"Gemini returned an empty response. Full response: {response}"
        )

    return text.strip()

if __name__ == "__main__":
    from metrics import (
        load_sales_data,
        get_daily_snapshot,
        get_weekly_comparison,
        get_top_performers,
    )

    print("Loading data and computing metrics...")
    df = load_sales_data()
    daily = get_daily_snapshot(df)
    weekly = get_weekly_comparison(df)
    performers = get_top_performers(df)

    print("Calling Gemini API...")
    summary = generate_summary(daily, weekly, performers)

    print("\n" + "=" * 60)
    print("AI-GENERATED BUSINESS REPORT")
    print("=" * 60)
    print(summary)
    print("=" * 60)
    print(f"\n✓ Report generated. Length: {len(summary)} chars.")