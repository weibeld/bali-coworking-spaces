import os
import sys
from google import genai
from dotenv import load_dotenv

# 1. Load the API key from engine/.env
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_key_here":
    print("❌ Error: GEMINI_API_KEY not found or not set in engine/.env")
    sys.exit(1)

# 2. Initialize the Gemini Client (AI Studio path)
client = genai.Client(api_key=api_key)

# 3. Simple Hello World Prompt
print("🚀 Sending 'Hello World' to Gemini...")

try:
    # We use gemini-flash-latest as verified in our earlier list_models.py test
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="Say hello to the Datapilot project! Keep it concise and professional."
    )
    
    print("\n🤖 Gemini's Response:")
    print("-" * 20)
    print(response.text)
    print("-" * 20)
    print("\n✅ LLM Communication Verified!")

except Exception as e:
    print(f"❌ Error communicating with Gemini: {e}")
