from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient

# ------------------ MCP Client ------------------
# connects to the AWS Documentation MCP server

aws_docs_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)

# ------------------ System Prompts ------------------
# MCP system prompt

SYSTEM_PROMPT = """
You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. You can querying the AWS Documentation.
"""

# ------------------ Agents ------------------

with aws_docs_client:
    all_tools = aws_docs_client.list_tools_sync()
    agent = Agent(tools=all_tools, system_prompt=SYSTEM_PROMPT)

    response = agent(
        "Get the documentation for AWS Lambda"
    )