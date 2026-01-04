from openai import AzureOpenAI
from app.config.settings import settings
import json
import re

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)


def _safe_parse_json(text: str):
    """
    Safely extract and parse JSON from LLM output.
    Handles invalid escapes caused by code / paths.
    """
    # First attempt: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Extract JSON block
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        raise ValueError("No JSON array found in LLM output")

    cleaned = match.group(0)

    # Fix common escape issues
    cleaned = cleaned.replace("\\", "\\\\")
    cleaned = cleaned.replace("\n", "\\n")
    cleaned = cleaned.replace("\t", "\\t")

    return json.loads(cleaned)


def generate_solution(repo_context: str, issue, partial: bool = False):
    partial_note = ""
    if partial:
        partial_note = """
IMPORTANT:
The repository analysis is still IN PROGRESS.
- Repository context may be partial
- Prefer conceptual guidance
- Avoid guessing exact file paths
- If unsure, explain assumptions clearly
"""

    prompt = f"""
You are a senior open-source contributor mentoring a first-time contributor.

{partial_note}

REPOSITORY CONTEXT:
{repo_context}

GITHUB ISSUE:
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
- Output STRICT JSON ONLY
- No explanations outside JSON
- If a file does not exist, clearly say CREATE it
- Use shell commands where applicable
- Be realistic and precise

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

    # Remove markdown fences if present
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    parsed = _safe_parse_json(content)

    if not isinstance(parsed, list):
        raise ValueError("AI response must be a list of steps")

    return parsed
