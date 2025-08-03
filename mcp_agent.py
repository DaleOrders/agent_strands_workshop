from fastapi import FastAPI
from pydantic import BaseModel
from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import http_request

# 🧠 System prompt: guides agent behavior
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

# 🛠 Custom tool: count words in final response
@tool
def word_count(text: str) -> int:
    """Count words in the given text."""
    return len(text.split())

# 🤖 Model configuration: Bedrock Claude 3.5 Haiku
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.3,
)

# 🧠 AI Agent setup
agent = Agent(
    name="GeoAgent",
    description="Finds country info and counts words using Wikipedia",
    model=bedrock_model,
    tools=[http_request, word_count],
    system_prompt=COUNTRY_INFO_SYSTEM_PROMPT,
)

# 🌐 FastAPI app setup
app = FastAPI(title="Strands GeoAgent MCP")

# 📦 Request schema
class PromptRequest(BaseModel):
    prompt: str

# 🎯 POST endpoint to run the agent
@app.post("/ask")
async def ask_agent(request: PromptRequest):
    try:
        response = agent(request.prompt)
        return {"response": str(response)}
    except Exception as e:
        return {"error": str(e)}


