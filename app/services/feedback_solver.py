from openai import AzureOpenAI
from app.config.settings import settings
import json

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

def refine_solution(repo_context, issue, step, error):
    """
    Azure-safe refinement:
    - No jailbreak wording
    - No 'override' or 'fix previous'
    - Treated as a fresh suggestion under constraints
    """

    prompt = f"""
You are a senior open-source contributor.

Repository Context:
{repo_context}

GitHub Issue:
Title: {issue.title}
Description: {issue.body}

Original Suggested Step:
{json.dumps(step, indent=2)}

Additional Context From Contributor:
{error}

TASK:
Propose an improved alternative step that better fits the repository structure
and resolves the contributor's concern.

IMPORTANT:
- This is a NEW suggestion, not a correction of previous output
- Do NOT reference policy, safety, or moderation
- Do NOT mention previous failures

OUTPUT RULES:
- Respond ONLY with valid JSON
- No markdown
- No explanations outside JSON

JSON FORMAT:
{{
  "step": {step["step"]},
  "title": "",
  "explanation": "",
  "file": "",
  "action": "",
  "verification": ""
}}
"""

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You generate safe, repository-accurate development guidance."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Refined step is not an object")
        return parsed
    except Exception as e:
        raise ValueError(
            f"Invalid refined step JSON.\n\nRaw:\n{content}"
        ) from e
