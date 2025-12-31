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

STRICT RULES:
- Respond ONLY with valid JSON
- Do NOT include markdown
- Do NOT include explanations outside JSON
- Do NOT wrap response in ```json

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

    # 🛡️ Remove markdown fences if Azure adds them
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(content)

        # Extra safety check
        if not isinstance(parsed, list):
            raise ValueError("AI response is not a list")

        return parsed

    except Exception as e:
        raise ValueError(
            f"AI returned invalid JSON.\n\nRaw response:\n{content}"
        ) from e
