def refine_solution(repo_context, issue, step, error):
    prompt = f"""
The previous solution step failed.

Repository Context:
{repo_context}

Issue:
{issue.title}

Original Step:
{step}

User Error Output:
{error}

Generate a corrected version of ONLY this step.
"""

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    return response.choices[0].message.content
