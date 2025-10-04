# check_models.py
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("Fetching available models from Groq...")

    models = client.models.list()

    print("\n--- Currently Available Models ---")
    for model in models.data:
        print(model.id)
    print("----------------------------------\n")

except Exception as e:
    print(f"An error occurred: {e}")