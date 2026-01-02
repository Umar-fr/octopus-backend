from openai import AzureOpenAI
from app.config.settings import settings
import json

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

def generate_solution(repo_context: str, issue):
    prompt = f"""
You are a senior open-source contributor.

{repo_context}

GitHub Issue:
Title: {issue.title}
Description: {issue.body}

TASK:
Generate a precise, contribution-ready solution.

RULES:
- Reference REAL file paths from the repo
- Be concise and actionable
- Respond ONLY with valid JSON
- No markdown
- No explanations outside JSON

JSON FORMAT:
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

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    parsed = json.loads(content)

    if not isinstance(parsed, list):
        raise ValueError("AI response is not a list")

    return parsed
