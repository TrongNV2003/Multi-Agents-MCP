import uvicorn
from loguru import logger
from fastapi import FastAPI, Query
from contextlib import asynccontextmanager

from multi_agents.pipeline import MultiAgents

async def startup_hook(app: FastAPI):
    app.state.multi_agents = MultiAgents()

    logger.info("Multi Agents is starting up...")

async def shutdown_hook(app: FastAPI):
    app.state.multi_agents = None

    logger.info("Multi Agents is shutting down...")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_hook(app)
    yield
    await shutdown_hook(app)
    
app = FastAPI(
    title="Multi Agents Function Calling",
    description="Self-built Multi Function calling AI Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
    )

@app.get("/chat", summary="Chat with Multi Agents")
async def chat(
    query: str = Query(..., description="User query to chat with the agents"),
    initial_context_data: dict = Query(default=None, description="Initial context data for the agents")
):
    """
    Chat with the multi-agents system.
    
    Args:
        query (str): The user query to chat with the agents.
        
    Returns:
        dict: The response from the multi-agents system.
    """
    response = await app.state.multi_agents.run(query, initial_context_data=initial_context_data)
    return {"response": response}

if __name__ == "__main__":
    logger.info("Starting Multi Agents Function Calling server...")
    uvicorn.run(app, host="0.0.0.0", port=2206)