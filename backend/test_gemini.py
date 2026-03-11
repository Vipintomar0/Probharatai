import sys
import os

# Add backend directory to sys.path so we can import llm
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.gemini import GeminiAdapter

def main():
    api_key = "AIzaSyDinifEwQ6SV2FCECBAHLCbLDYYUh1GWXk"
    try:
        adapter = GeminiAdapter(api_key=api_key)
        
        messages = [
            {"role": "user", "content": "Hello! Can you write a very short haiku about artificial intelligence?"}
        ]
        
        print(f"Sending request to Gemini using the provided API key...")
        response = adapter.chat(messages)
        print("\nGemini Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
