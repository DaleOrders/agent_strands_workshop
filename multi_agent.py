from fastapi import FastAPI
from pydantic import BaseModel
from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import http_request

# ------------------ System Prompts ------------------

# 🌍 GeoAgent system prompt
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

# 💱 CurrencyAgent system prompt
CURRENCY_CONVERT_SYSTEM_PROMPT = """You are a currency converter assistant.

1. You convert New Zealand Dollars (NZD) into the currency of a given country.
2. Use this exchange rate API endpoint format:
   https://api.exchangerate.host/convert?from=NZD&to={currency_code}
3. Return only the conversion result in your reply.

You must look up the correct 3-letter currency code for the country requested. If the country is ambiguous or not supported, say so clearly.
"""

# ------------------ Tools ------------------

@tool
def word_count(text: str) -> int:
    """Count words in the given text."""
    return len(text.split())

# ------------------ Model ------------------

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.3,
)

# ------------------ Agents ------------------

geo_agent = Agent(
    name="GeoAgent",
    description="Finds country info and counts words using Wikipedia",
    model=bedrock_model,
    tools=[http_request, word_count],
    system_prompt=COUNTRY_INFO_SYSTEM_PROMPT,
)

currency_agent = Agent(
    name="CurrencyAgent",
    description="Converts NZD to another country's currency",
    model=bedrock_model,
    tools=[http_request],
    system_prompt=CURRENCY_CONVERT_SYSTEM_PROMPT,
)

# ------------------ Orchestrator ------------------

def orchestrator(prompt: str):
    prompt_lower = prompt.lower()
    if "convert" in prompt_lower or "nzd" in prompt_lower or "currency" in prompt_lower:
        return currency_agent(prompt)
    else:
        return geo_agent(prompt)

# ------------------ FastAPI App ------------------

app = FastAPI(title="Strands Orchestrator MCP")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask")
async def ask_mcp(request: PromptRequest):
    try:
        response = orchestrator(request.prompt)
        return {"response": str(response)}
    except Exception as e:
        return {"error": str(e)}

