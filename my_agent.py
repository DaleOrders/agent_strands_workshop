from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import http_request

# System prompt
COUNTRY_INFO_SYSTEM_PROMPT = """You are a geography assistant with HTTP capabilities. You can:

1. Make HTTP requests to public APIs or Wikipedia to gather country information
2. Provide the capital city and a short description of the country
3. Use the word_count tool to count how many words are in your full response

To gather information:
- Use this format: https://en.wikipedia.org/api/rest_v1/page/summary/{country_name}
- Replace spaces with underscores (e.g., "New Zealand" → "New_Zealand")
- If the response is a disambiguation page, try with "{country_name} (country)"

When responding:
- Clearly state the capital city
- Include a concise, human-friendly description of the country
- End with the total word count of your full response
- Handle errors gracefully if the country is not found or response is ambiguous
"""

# Tool: count words
@tool
def word_count(text: str) -> int:
    return len(text.split())

# Bedrock model config
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.3,
)

# Agent setup
agent = Agent(
    name="GeoAgent",
    description="Finds country info and counts words using Wikipedia",
    model=bedrock_model,
    tools=[http_request, word_count],
    system_prompt=COUNTRY_INFO_SYSTEM_PROMPT,
)

# Ask the agent from CLI
if __name__ == "__main__":
    while True:
        prompt = input("Ask about a country: ")
        if prompt.lower() in {"exit", "quit"}:
            break
        response = agent(prompt)
        print("Response:", response)
