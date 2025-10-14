
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Setup ---
print("Attempting to load .env file from the current directory...")

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("\n--- ERROR ---")
    print("Could not find the GOOGLE_API_KEY in your .env file.")
    print("Please ensure the .env file is in the same directory as this script and the key is correct.")
else:
    print("API Key found. Configuring the client...")
    genai.configure(api_key=api_key)

    
    print("\nFetching a list of models you have access to...")
    print("--------------------------------------------------")
    
    found_models = False
    try:
        for m in genai.list_models():
            
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Found usable model: {m.name}")
                found_models = True
    except Exception as e:
        print(f"\n--- ERROR ---")
        print(f"An error occurred while trying to fetch the models: {e}")

    if not found_models:
        print("\n--- RESULT ---")
        print("Could not find any usable models that support 'generateContent'.")
        print("This strongly suggests an issue with your Google AI project setup or API key permissions.")
        print("Please try generating a new API key in Google AI Studio and ensure the 'Generative Language API' is enabled.")