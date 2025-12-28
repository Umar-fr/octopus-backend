from openai import AzureOpenAI
from app.config.settings import settings
import json

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

def generate_solution(repo_context, issue):
    prompt = f"""
You are a senior software engineer.

Repository Context:
{repo_context}

GitHub Issue:
Title: {issue.title}
Description: {issue.body}

Generate a step-by-step solution.
Each step must include:
- Explanation
- What file to modify
- What change to make
- How to verify the fix

Respond in JSON with this structure:
[
  {{
    "step": 1,
    "title": "",
    "explanation": "",
    "file": "",
    "action": "",
    "verification": ""
  }}
]
"""

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    return json.loads(response.choices[0].message.content)
