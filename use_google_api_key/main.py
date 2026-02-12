import os
import sys
from dotenv import load_dotenv
from google import genai

def main():
    # 1. Load environment variables from .env
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    model_id = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash-lite")
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Error: GOOGLE_API_KEY not found in .env file.")
        print("Please update your .env file with a valid Google AI Studio API key.")
        sys.exit(1)

    # 2. Read prompt.md content
    prompt_path = "prompt.md"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_text = f.read()
    except FileNotFoundError:
        print(f"Error: {prompt_path} not found.")
        sys.exit(1)

    print(f"--- Calling Gemini Model: {model_id} ---")
    
    # 3. Initialize Google GenAI Client
    client = genai.Client(api_key=api_key)
    
    # 4. Generate Content
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt_text
        )
        
        # 5. Output Response
        print("\n--- Response ---")
        print(response.text)
        
    except Exception as e:
        print(f"An error occurred during API call: {e}")

if __name__ == "__main__":
    main()
