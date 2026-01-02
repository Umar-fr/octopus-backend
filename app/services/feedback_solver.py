from openai import AzureOpenAI
from app.config.settings import settings
import json

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

def refine_solution(repo_context, issue, step, error):
    prompt = f"""
You are a senior software engineer fixing a failed implementation step.

Repository Context:
{repo_context}

GitHub Issue:
Title: {issue.title}
Description: {issue.body}

FAILED STEP (JSON):
{json.dumps(step, indent=2)}

USER ERROR:
{error}

TASK:
Return a corrected version of ONLY this step.

STRICT RULES:
- Respond ONLY with valid JSON
- Do NOT include markdown
- Do NOT include explanations outside JSON
- Do NOT wrap response in ```json

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
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    content = response.choices[0].message.content.strip()

    # 🛡️ Strip accidental markdown
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    # Validate JSON
    try:
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Refined step is not an object")
        return parsed
    except Exception as e:
        raise ValueError(
            f"AI returned invalid refined step JSON.\n\nRaw:\n{content}"
        ) from e
