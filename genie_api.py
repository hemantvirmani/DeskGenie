"""FastAPI backend for DeskGenie."""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import os

import config
from agents import MyGAIAAgents
from agent_runner import AgentRunner

# Initialize FastAPI app
app = FastAPI(
    title="DeskGenie API",
    description="Desktop AI Agent API",
    version="1.0.0"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],  # Vite dev server + production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store for active tasks (in production, use Redis or similar)
tasks_store = {}

# --- Pydantic Models ---

class ChatRequest(BaseModel):
    message: str
    file_name: Optional[str] = None
    agent_type: Optional[str] = None

class ChatResponse(BaseModel):
    task_id: str
    status: str

class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "running", "completed", "error"
    result: Optional[str] = None
    error: Optional[str] = None

class ToolInfo(BaseModel):
    name: str
    description: str
    category: str

class ConfigInfo(BaseModel):
    active_agent: str
    available_agents: list[str]
    ollama_enabled: bool
    desktop_tools_enabled: bool
    ollama_model: str

# --- API Endpoints ---

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "DeskGenie"}

@app.get("/api/config", response_model=ConfigInfo)
async def get_config():
    """Get current configuration."""
    return ConfigInfo(
        active_agent=config.ACTIVE_AGENT,
        available_agents=[config.AGENT_LANGGRAPH, config.AGENT_REACT_LANGGRAPH],
        ollama_enabled=config.ENABLE_OLLAMA,
        desktop_tools_enabled=config.ENABLE_DESKTOP_TOOLS,
        ollama_model=config.OLLAMA_DEFAULT_MODEL
    )

@app.get("/api/tools", response_model=list[ToolInfo])
async def get_tools():
    """Get list of available tools."""
    tools = []

    # Get tool categories from config
    for category, tool_names in config.TOOL_CATEGORIES.items():
        for tool_name in tool_names:
            tools.append(ToolInfo(
                name=tool_name,
                description=f"{tool_name.replace('_', ' ').title()}",
                category=category
            ))

    return tools

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent and get a task ID for tracking."""
    task_id = str(uuid.uuid4())

    # Store task as pending
    tasks_store[task_id] = {
        "status": "pending",
        "result": None,
        "error": None
    }

    # Run agent in background
    asyncio.create_task(run_agent_task(
        task_id=task_id,
        message=request.message,
        file_name=request.file_name,
        agent_type=request.agent_type
    ))

    return ChatResponse(task_id=task_id, status="pending")

async def run_agent_task(task_id: str, message: str, file_name: str = None, agent_type: str = None):
    """Run agent task in background."""
    try:
        tasks_store[task_id]["status"] = "running"

        # Run agent in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        agent = MyGAIAAgents(active_agent=agent_type)
        result = await loop.run_in_executor(
            None,
            lambda: agent(message, file_name)
        )

        tasks_store[task_id]["status"] = "completed"
        tasks_store[task_id]["result"] = result

    except Exception as e:
        tasks_store[task_id]["status"] = "error"
        tasks_store[task_id]["error"] = str(e)

@app.get("/api/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of a running task."""
    if task_id not in tasks_store:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_store[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        result=task["result"],
        error=task["error"]
    )

@app.post("/api/chat/sync")
async def chat_sync(request: ChatRequest):
    """Synchronous chat endpoint (waits for response)."""
    try:
        loop = asyncio.get_event_loop()
        agent = MyGAIAAgents(active_agent=request.agent_type)
        result = await loop.run_in_executor(
            None,
            lambda: agent(request.message, request.file_name)
        )
        return {"status": "completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Static Files (Production) ---

# Check if frontend build exists
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    # Serve static files from React build
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        """Serve React frontend."""
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        """Serve React frontend for all routes (SPA support)."""
        # Check if it's an API route
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        # Serve index.html for all other routes
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Frontend not found")
