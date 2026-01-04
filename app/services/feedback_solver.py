from openai import AzureOpenAI
from app.config.settings import settings
import json
import re
from app.models.issue import Issue

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

def clean_json_response(response: str) -> str:
    """
    Extract JSON from LLM response that might contain markdown or extra text.
    """
    # Remove markdown code blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    
    # Find JSON array or object
    # Look for [ ... ] or { ... }
    json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', response)
    if json_match:
        return json_match.group(1).strip()
    
    # If no match, return cleaned response
    return response.strip()


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
Improve the following implementation step based on user feedback.

CONSTRAINTS:
- Maintain repository accuracy
- Do not invent file paths
- JSON ONLY

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
    content = clean_json_response(content)

    try:
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Refined step is not an object")
        return parsed
    except Exception as e:
        raise ValueError(
            f"Invalid refined step JSON.\n\nRaw:\n{content}"
        ) from e


def regenerate_subsequent_steps(
    repo_context: str,
    issue: Issue,
    completed_steps: list,
    starting_step_number: int,
    total_steps: int
) -> list:
    """
    Regenerate all steps after the refined one, given the context
    of what was done before.
    """
    
    # Build context from completed steps
    steps_context = "\n".join([
        f"Step {s['step']}: {s.get('action', s.get('title', s.get('description', '')))}"
        for s in completed_steps
    ])
    
    prompt = f"""
You are a senior open-source contributor providing step-by-step implementation guidance.

Repository Context:
{repo_context}

GitHub Issue:
Title: {issue.title}
Description: {issue.body}

Steps completed so far:
{steps_context}

TASK:
Generate the remaining {total_steps - starting_step_number + 1} steps (starting from step {starting_step_number}) 
to complete the solution. Ensure the steps logically follow from what's been done.

OUTPUT RULES:
- Respond ONLY with a valid JSON array
- No markdown code blocks
- No explanations outside JSON
- Each step must be a complete, actionable instruction

JSON FORMAT:
[
  {{
    "step": {starting_step_number},
    "title": "Brief step title",
    "action": "Detailed description of what to do",
    "file": "path/to/file.ext (if applicable)",
    "code": "code snippet if needed",
    "verification": "How to verify this step worked"
  }}
]
"""

    try:
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You generate safe, repository-accurate development guidance."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        content = clean_json_response(content)
        
        new_steps = json.loads(content)
        
        # Validate it's a list
        if not isinstance(new_steps, list):
            raise ValueError("Response is not a list")
        
        # Ensure step numbers are correct and required fields exist
        for i, step in enumerate(new_steps):
            if "step" not in step:
                step["step"] = starting_step_number + i
            # Ensure required fields exist with defaults
            step.setdefault("title", f"Step {step['step']}")
            step.setdefault("action", "")
            step.setdefault("code", "")
            step.setdefault("file", "")
            step.setdefault("explanation", step.get("action", ""))
            step.setdefault("verification", "")
        
        return new_steps
        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Error parsing LLM response for subsequent steps: {e}")
        print(f"Raw response: {content[:500] if 'content' in locals() else 'No response'}")
        
        # Fallback: return continuation steps
        remaining_count = total_steps - starting_step_number + 1
        return [
            {
                "step": starting_step_number + i,
                "title": f"Continue implementation (step {starting_step_number + i})",
                "action": "Continue implementation based on previous steps",
                "explanation": "Automated fallback step due to generation error",
                "code": "",
                "file": "",
                "verification": ""
            }
            for i in range(remaining_count)
        ]