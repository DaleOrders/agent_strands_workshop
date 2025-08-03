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


## Step 4: Create MCP strands agent using integrated with AWS 

Create a file called 'mcp_docs.py'

```
touch mcp_docs.py
````

Paste in the following code:

```
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

aws_docs_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)

aws_diag_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.aws-diagram-mcp-server@latest"]
        )
    )
)


bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.7,
)

SYSTEM_PROMPT = """
You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. You can querying the AWS Documentation and generate diagrams. Make sure to tell the customer the full file path of the diagram.
"""

with aws_diag_client, aws_docs_client:
    all_tools = aws_diag_client.list_tools_sync() + aws_docs_client.list_tools_sync()
    agent = Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)

    response = agent(
        "Get the documentation for AWS Lambda then create a diagram of a website that uses AWS Lambda for a static website hosted on S3"
    )

````

Test the agent

```
python3 mcp_docs.py

````

## Step 5: Multi-agent Strands Design