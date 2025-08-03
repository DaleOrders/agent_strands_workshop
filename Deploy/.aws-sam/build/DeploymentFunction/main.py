import logging
from fastapi import FastAPI
from pydantic import BaseModel
from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import http_request

# ------------------ Setup logging ------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("holiday_workflow")

# ------------------ System Prompts ------------------

# Agent 1: Find a holiday destination based on user preferences
HOLIDAY_DESTINATION_PROMPT = """You are an expert travel assistant.

Given this user input, recommend a single ideal holiday destination (city and country).
Be concise and clear.
"""

# Agent 2: Create an itinerary for the holiday destination
ITINERARY_PROMPT = """You are a travel planner assistant.

Given a holiday destination, create a detailed 5-day itinerary for a tourist visiting this location.
Include key activities, places to visit, and tips.
"""

# Agent 3: Create a budget for the holiday
BUDGET_PROMPT = """You are a budget planning assistant.

Given a 5-day holiday itinerary for a destination, create a detailed budget estimate including accommodation, food, transport, and activities.
Provide costs in USD.
"""

# ------------------ Tools ------------------

@tool
def word_count(text: str) -> int:
    return len(text.split())

# ------------------ Model ------------------

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.3,
)

# ------------------ Agents ------------------

agent_1 = Agent(
    name="HolidayDestinationAgent",
    description="Finds an ideal holiday destination from user input",
    model=bedrock_model,
    system_prompt=HOLIDAY_DESTINATION_PROMPT,
)

agent_2 = Agent(
    name="ItineraryAgent",
    description="Creates a 5-day itinerary for a given holiday destination",
    model=bedrock_model,
    system_prompt=ITINERARY_PROMPT,
)

agent_3 = Agent(
    name="BudgetAgent",
    description="Creates a budget estimate for a 5-day holiday itinerary",
    model=bedrock_model,
    system_prompt=BUDGET_PROMPT,
)

# ------------------ Workflow Orchestrator ------------------

def orchestrator(user_input: str):
    logger.info(f"Workflow started with input: {user_input}")

    # Step 1: Find holiday destination
    prompt_1 = f"{user_input}\nPlease recommend a single holiday destination."
    destination = agent_1(prompt_1)
    logger.info(f"Agent 1 found destination: {destination}")

    # Step 2: Create itinerary for destination
    prompt_2 = f"Destination: {destination}\nPlease create a 5-day itinerary."
    itinerary = agent_2(prompt_2)
    logger.info(f"Agent 2 created itinerary:\n{itinerary}")

    # Step 3: Create budget for itinerary
    prompt_3 = f"Itinerary:\n{itinerary}\nPlease create a budget for a 5-day holiday."
    budget = agent_3(prompt_3)
    logger.info(f"Agent 3 created budget:\n{budget}")

    # Combine all outputs
    final_response = (
        f"Holiday Destination:\n{destination}\n\n"
        f"5-Day Itinerary:\n{itinerary}\n\n"
        f"Budget Estimate:\n{budget}"
    )

    logger.info("Workflow completed successfully")
    return final_response

# ------------------ FastAPI App ------------------

app = FastAPI(title="Holiday Planning Workflow MCP")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask")
async def ask_mcp(request: PromptRequest):
    logger.info(f"Received request with prompt: {request.prompt}")
    try:
        response = orchestrator(request.prompt)
        logger.info("Request processed successfully")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return {"error": str(e)}

# ------------------ AWS Lambda Handler ------------------

from mangum import Mangum
handler = Mangum(app)
