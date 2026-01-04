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
You are a senior open-source contributor mentoring a first-time contributor.

{repo_context}

GitHub Issue:
Title: {issue.title}
Description: {issue.body}

TASK:
Produce a FULL contribution workflow.

MANDATORY WORKFLOW:
0. Clone repository
1. Create a feature branch
2. Locate or create relevant files
3. Implement fix
4. Test locally
5. Commit changes
6. Push branch
7. Open Pull Request

STRICT RULES:
- ONLY use file paths from the repository tree
- If a file is missing, explicitly instruct to CREATE it
- Include shell commands where applicable
- Be realistic and precise
- JSON ONLY

OUTPUT FORMAT:
[
  {{
    "step": 0,
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
        messages=[
            {"role": "system", "content": "You generate precise, repository-grounded contribution steps."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.05
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    parsed = json.loads(content)

    if not isinstance(parsed, list):
        raise ValueError("AI response must be a list")

    return parsed