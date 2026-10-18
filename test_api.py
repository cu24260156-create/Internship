import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

print("=" * 60)
print(" InternBot - Gemini API Key Verification Tool")
print("=" * 60)

# Load .env
env_path = Path(__file__).resolve().parent / ".env"
if not env_path.exists():
    print(f"\n❌ ERROR: .env file not found at {env_path}")
    sys.exit(1)

load_dotenv(dotenv_path=env_path, override=True)
api_key = os.getenv("GEMINI_API_KEY", "").strip()

print(f"\n1. Checking .env file:")
print(f"   - File location: {env_path}")
print(f"   - Key found in .env: {bool(api_key)}")

if not api_key:
    print("\n❌ FAILED: GEMINI_API_KEY is empty.")
    print("👉 Solution: Open .env and set GEMINI_API_KEY=your_key_here")
    print("👉 Get a free key at: https://aistudio.google.com/apikey")
    sys.exit(1)

# Check placeholders
upper_key = api_key.upper()
if any(p in upper_key for p in ["PASTE_", "YOUR_", "EXAMPLE", "API_KEY_HERE"]):
    print(f"\n❌ FAILED: GEMINI_API_KEY is still a placeholder value: '{api_key}'")
    print("👉 Solution: Replace it in .env with your actual key from Google AI Studio.")
    print("👉 Get your key here: https://aistudio.google.com/apikey")
    sys.exit(1)

print(f"   - Key length: {len(api_key)} characters")

if len(api_key) < 30:
    print(f"\n⚠️ WARNING: Key length is {len(api_key)}. Google Gemini API keys are typically ~39 characters (starting with AIza).")

# Test live API call
print("\n2. Testing connection to Google Gemini API...")

try:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    models_to_test = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    success = False

    for model in models_to_test:
        try:
            print(f"   - Trying model '{model}'...")
            response = client.models.generate_content(
                model=model,
                contents="Reply with: Gemini API connection successful!"
            )
            reply = (response.text or "").strip()
            print(f"\n✅ SUCCESS! Google Gemini API responded using '{model}':")
            print(f"   AI Output: {reply}")
            print("\n🎉 Your API key is 100% valid and working!")
            success = True
            break
        except Exception as e:
            err_str = str(e)
            if "not found" in err_str.lower() or "not supported" in err_str.lower():
                print(f"     Model '{model}' not available for your key, trying next...")
                continue
            else:
                raise e

    if not success:
        print("\n❌ Could not connect using tested flash models.")

except Exception as e:
    err_msg = str(e)
    err_type = type(e).__name__
    print(f"\n❌ API TEST FAILED: {err_type}")
    print(f"Details: {err_msg}")

    if "API_KEY_INVALID" in err_msg or "400" in err_msg:
        print("\n👉 Root Cause: Google rejected the key as invalid (400 INVALID_ARGUMENT).")
        print("👉 Solution:")
        print("   1. Go to: https://aistudio.google.com/apikey")
        print("   2. Click 'Create API key' (or copy an existing active key)")
        print("   3. Paste the complete 39-character key into .env: GEMINI_API_KEY=AIzaSy...")
        print("   4. Re-run: python test_api.py")
    elif "quota" in err_msg.lower() or "429" in err_msg:
        print("\n👉 Root Cause: Rate limit or quota exceeded.")
    else:
        print(f"\n👉 Check network or proxy settings.")
