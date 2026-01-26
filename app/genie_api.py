"""FastAPI backend for DeskGenie."""

import sys
from pathlib import Path

# Add project root to path for direct script execution
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import asyncio
import json
import signal
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import os

from app import config
from agents.agents import MyGAIAAgents
from runners.question_runner import run_gaia_questions
from utils.langfuse_tracking import track_session
from utils.log_streamer import LogStreamer, create_logger, set_global_logger
from resources.ui_strings import APIStrings as S

# Track background tasks for cleanup
_background_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    print("[API] Server starting...")
    # Set global logger to LogStreamer for UI mode (no console output)
    set_global_logger(LogStreamer(task_id="global", console_output=False))
    yield
    # Cleanup on shutdown
    print("[API] Server shutting down, cancelling background tasks...")
    for task in _background_tasks:
        task.cancel()
    if _background_tasks:
        await asyncio.gather(*_background_tasks, return_exceptions=True)
    _background_tasks.clear()
    print("[API] Shutdown complete.")


# Initialize FastAPI app
app = FastAPI(
    title="DeskGenie API",
    description="Desktop AI Agent API",
    version="1.0.0",
    lifespan=lifespan
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

class BenchmarkRequest(BaseModel):
    filter_indices: Optional[list[int]] = None  # e.g., [0, 2, 5] or None for all
    agent_type: Optional[str] = None

class BenchmarkResponse(BaseModel):
    task_id: str
    status: str

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
        available_agents=[config.AGENT_LANGGRAPH, config.AGENT_REACT_LANGGRAPH]
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

    # Run agent in background (track for cleanup)
    task = asyncio.create_task(run_agent_task(
        task_id=task_id,
        message=request.message,
        file_name=request.file_name,
        agent_type=request.agent_type
    ))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    return ChatResponse(task_id=task_id, status="pending")

async def run_agent_task(task_id: str, message: str, file_name: str = None, agent_type: str = None):
    """Run agent task in background."""
    logger = create_logger(task_id, streaming=True)

    try:
        tasks_store[task_id]["status"] = "running"
        logger.info("=" * 60)

        start_time = time.time()

        # Run agent in thread pool to avoid blocking with Langfuse tracking
        loop = asyncio.get_event_loop()

        def execute_with_tracking():
            with track_session("Chat_Request", {
                "task_id": task_id,
                "agent_type": agent_type or config.ACTIVE_AGENT,
                "has_file": file_name is not None,
                "message_length": len(message),
                "mode": "chat"
            }):
                agent = MyGAIAAgents(active_agent=agent_type, logger=logger)
                return agent(message, file_name)

        result = await loop.run_in_executor(None, execute_with_tracking)

        # Calculate runtime
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        tasks_store[task_id]["status"] = "completed"
        tasks_store[task_id]["result"] = result
        logger.success(S.CHAT_COMPLETED_WITH_TIME.format(minutes=minutes, seconds=seconds))

    except Exception as e:
        tasks_store[task_id]["status"] = "error"
        tasks_store[task_id]["error"] = str(e)
        logger.error(S.CHAT_FAILED.format(error=str(e)))
    finally:
        logger.close()

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

        def execute_with_tracking():
            with track_session("Chat_Sync", {
                "agent_type": request.agent_type or config.ACTIVE_AGENT,
                "has_file": request.file_name is not None,
                "message_length": len(request.message),
                "mode": "chat_sync"
            }):
                agent = MyGAIAAgents(active_agent=request.agent_type)
                return agent(request.message, request.file_name)

        result = await loop.run_in_executor(None, execute_with_tracking)
        return {"status": "completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Benchmark Endpoints ---

@app.post("/api/benchmark", response_model=BenchmarkResponse)
async def run_benchmark(request: BenchmarkRequest):
    """Run benchmark tests on GAIA questions."""
    task_id = str(uuid.uuid4())

    # Store task as pending
    tasks_store[task_id] = {
        "status": "pending",
        "result": None,
        "error": None
    }

    # Run benchmark in background (track for cleanup)
    task = asyncio.create_task(run_benchmark_task(
        task_id=task_id,
        filter_indices=request.filter_indices,
        agent_type=request.agent_type
    ))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    return BenchmarkResponse(task_id=task_id, status="pending")

async def run_benchmark_task(task_id: str, filter_indices: list = None, agent_type: str = None):
    """Run benchmark task in background."""
    # Create logger for this task
    logger = create_logger(task_id, streaming=True)

    try:
        tasks_store[task_id]["status"] = "running"

        # Convert list to tuple if provided
        filter_tuple = tuple(filter_indices) if filter_indices else None
        question_desc = f"indices {filter_indices}" if filter_indices else "all questions"
        logger.info(S.STARTING_BENCHMARK.format(description=question_desc))

        # Run benchmark in thread pool to avoid blocking with Langfuse tracking
        loop = asyncio.get_event_loop()

        def execute_with_tracking():
            with track_session("Benchmark_Run", {
                "task_id": task_id,
                "agent_type": agent_type or config.ACTIVE_AGENT,
                "filter_indices": str(filter_indices) if filter_indices else "all",
                "question_count": len(filter_indices) if filter_indices else "all",
                "mode": "benchmark"
            }):
                run_gaia_questions(filter=filter_tuple, active_agent=agent_type, logger=logger)

        await loop.run_in_executor(None, execute_with_tracking)

        tasks_store[task_id]["status"] = "completed"
        tasks_store[task_id]["result"] = "Benchmark completed - see logs for details"
        logger.success(S.BENCHMARK_COMPLETED)

    except Exception as e:
        tasks_store[task_id]["status"] = "error"
        tasks_store[task_id]["error"] = str(e)
        logger.error(S.BENCHMARK_FAILED.format(error=str(e)))
    finally:
        logger.close()


# --- SSE Endpoints for Log Streaming ---

@app.get("/api/task/{task_id}/logs")
async def get_task_logs(task_id: str, since: float = 0):
    """Get logs for a task (polling endpoint)."""
    logger = LogStreamer.get(task_id)
    if not logger:
        return {"logs": []}
    return {"logs": logger.get_logs(since=since)}


@app.get("/api/task/{task_id}/logs/stream")
async def stream_task_logs(task_id: str):
    """Stream logs for a task via SSE."""

    async def event_generator():
        logger = LogStreamer.get(task_id)

        # Wait for logger to be created (task may not have started yet)
        wait_count = 0
        while not logger and wait_count < 50:  # Wait up to 5 seconds
            await asyncio.sleep(0.1)
            logger = LogStreamer.get(task_id)
            wait_count += 1

        if not logger:
            yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
            return

        # Subscribe to new logs
        queue = await logger.subscribe()

        try:
            # First, send any existing logs
            for log in logger.get_logs():
                yield f"data: {json.dumps(log)}\n\n"

            # Then stream new logs
            while True:
                try:
                    entry = await asyncio.wait_for(queue.get(), timeout=30.0)
                    if entry is None:  # Stream closed
                        break
                    yield f"data: {json.dumps(entry.to_dict())}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield f": keepalive\n\n"
        finally:
            logger.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

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
