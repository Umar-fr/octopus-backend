from openai import AzureOpenAI
from app.config.settings import settings

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

def classify_issue(title, body):
    prompt = f"""
Classify the GitHub issue into one of:
- Beginner
- Moderate
- Professional

Issue Title: {title}
Issue Description: {body}

Respond with only one word.
"""

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()
