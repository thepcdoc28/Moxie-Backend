import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=os.environ.get("NVIDIA_API_KEY")
)

try:
  completion = client.chat.completions.create(
    model="meta/llama-3.1-70b-instruct",
    messages=[{"role":"user","content":"hi"}],
    temperature=0.5,
    top_p=1,
    max_tokens=1024,
    stream=True
  )

  for chunk in completion:
    if chunk.choices[0].delta.content is not None:
      print(chunk.choices[0].delta.content, end="")
except Exception as e:
  print("ERROR:", e)
