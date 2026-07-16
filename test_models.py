import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=os.environ.get("NVIDIA_API_KEY")
)

models = [
    'meta/llama-3.1-405b-instruct',
    'meta/llama-3.1-70b-instruct', 
    'meta/llama-3.1-8b-instruct',
    'mistralai/mixtral-8x22b-instruct-v0.1',
    'google/gemma-2-27b-it',
    'nvidia/nemotron-4-340b-instruct'
]

working = []
failing = []

# Or use client.models.list()
try:
    available_models = client.models.list()
    print("Available models:")
    for m in available_models.data:
        print(" -", m.id)
except Exception as e:
    print("Could not list models:", e)

for model in models:
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":"hi"}],
            max_tokens=1
        )
        print(f"[OK] {model}")
        working.append(model)
    except Exception as e:
        print(f"[FAIL] {model}: {e}")
        failing.append(model)
