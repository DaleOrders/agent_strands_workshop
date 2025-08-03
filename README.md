# agent_strands_workshop
Community Day Virtual 2025 Workshop

This workshop includes step by step instructions to accompany the workshop 'AI Agents in Action: Build Cloud-Ready AI with AWS Strands' for Community Day Virtual NZD 2025


- Initializing a basic python structure
- Explore design stands agents using workflow, multi-agent and MCP patterns
- Deploying the agent to AWS using SAM


---

## Table of Contents

0. [Prerequisites](#prerequisites)
1. [Step 1: Initialize the Project](#step-1-initialize-the-project)


---

## Prerequisites


Before starting, ensure you have the following installed:

- **Node.js** (>= 14.x)
- **AWS CLI** (configures upon authorization)
- **AWS SAM** (>= 2.x)
- **Python**  (>= 3.x)
- **Claude Bedrock Model enabled**  (= 3.5)

---

## Step 1: Initialize the Project

Create the .venv environment

```
python3 -m venv .venv
```

Activates the Python virtual environment located in the .venv directory.

```
source .venv/bin/activate 
```

Install dependencies for this workshop

```
pip install openai fastapi uvicorn strands-agents strands-agents-tools "strands-agents[a2a]"
```

## Step 2: Create first strands Agent

Create a file called 'my_agent.py'

In root run:

```
touch my_agent.py
```

Inside my_agent.py paste the following code block

````
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

````

Test the code by running

```
python3 my_agent.py
```

## Step 3: Create MCP strands agent

Create mcp_agent.py file

```
touch mcp_agent.py
```

Paste the following code block into mcp_agent.py

```
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

````

Start the agent on port 8000

```
uvicorn mcp_agent:app --reload --port 8000

````

Test the agent by making an api calling using prompt (example prompt below).

In a new terminal

```
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me about New Zealand"}'

````
