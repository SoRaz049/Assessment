# In check_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the environment variables from your .env file
load_dotenv()

# Configure the API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=api_key)

print("Finding available models that support 'generateContent'...\n")

# List all models and filter for the ones we can use for chat/generation
for model in genai.list_models():
    # We check if 'generateContent' is one of the supported methods
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model name: {model.name}")

print("\nScript finished.")