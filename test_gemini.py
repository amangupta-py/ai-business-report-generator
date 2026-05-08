"""Quick test to verify Gemini API key is working."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    print("   Make sure .env exists in the project root with your key.")
    exit(1)

print(f"✓ API key loaded (starts with: {api_key[:8]}...)")

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content("Say 'API working' in one short sentence.")
    print(f"✓ Gemini response: {response.text.strip()}")
    print("✓ Setup is complete and working!")
except Exception as e:
    print(f"❌ Error calling Gemini: {e}")
    print("   Check that your API key is correct in .env")