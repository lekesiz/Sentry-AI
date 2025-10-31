"""
API routes for Sentry-AI.

This module provides a REST API for controlling and monitoring Sentry-AI.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

from ..core.config import settings
from ..core.database import db_manager
from ..models.data_models import SystemStatus


# Pydantic models for API requests/responses
class ActionLogResponse(BaseModel):
    """Response model for action logs."""
    id: int
    timestamp: datetime
    app_name: str
    dialog_type: str
    question: str
    chosen_option: str
    success: bool
    execution_time_ms: float


class StatisticsResponse(BaseModel):
    """Response model for statistics."""
    total_actions: int
    successful_actions: int
    failed_actions: int
    success_rate: float
    avg_execution_time_ms: float
    most_active_app: Optional[str]
    actions_by_app: dict


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates."""
    observer_interval: Optional[float] = None
    ollama_model: Optional[str] = None
    blacklist_apps: Optional[List[str]] = None


# Create FastAPI app
app = FastAPI(
    title="Sentry-AI API",
    description="REST API for Sentry-AI cognitive automation agent",
    version=settings.app_version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global state (in production, this would be managed differently)
_system_state = {
    "is_running": False,
    "start_time": None,
    "observer_active": False,
    "ollama_available": False,
    "actions_performed_today": 0
}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get the current system status."""
    uptime = 0.0
    if _system_state["start_time"]:
        uptime = (datetime.now() - _system_state["start_time"]).total_seconds()
    
    # Get last action timestamp from database
    recent_actions = db_manager.get_recent_actions(limit=1)
    last_action = recent_actions[0].timestamp if recent_actions else None
    
    return SystemStatus(
        is_running=_system_state["is_running"],
        observer_active=_system_state["observer_active"],
        ollama_available=_system_state["ollama_available"],
        actions_performed_today=_system_state["actions_performed_today"],
        last_action_timestamp=last_action,
        uptime_seconds=uptime
    )


@app.post("/start")
async def start_system():
    """Start the Sentry-AI system."""
    if _system_state["is_running"]:
        raise HTTPException(status_code=400, detail="System is already running")
    
    _system_state["is_running"] = True
    _system_state["start_time"] = datetime.now()
    _system_state["observer_active"] = True
    
    logger.info("System started via API")
    
    return {"status": "started", "timestamp": datetime.now().isoformat()}


@app.post("/stop")
async def stop_system():
    """Stop the Sentry-AI system."""
    if not _system_state["is_running"]:
        raise HTTPException(status_code=400, detail="System is not running")
    
    _system_state["is_running"] = False
    _system_state["observer_active"] = False
    
    logger.info("System stopped via API")
    
    return {"status": "stopped", "timestamp": datetime.now().isoformat()}


@app.get("/logs", response_model=List[ActionLogResponse])
async def get_logs(
    limit: int = Query(50, ge=1, le=500),
    app_name: Optional[str] = None
):
    """
    Get action logs.
    
    Args:
        limit: Maximum number of logs to return (1-500)
        app_name: Filter by application name (optional)
    """
    if app_name:
        logs = db_manager.get_actions_by_app(app_name, limit=limit)
    else:
        logs = db_manager.get_recent_actions(limit=limit)
    
    return [
        ActionLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            app_name=log.app_name,
            dialog_type=log.dialog_type,
            question=log.question,
            chosen_option=log.chosen_option,
            success=log.success,
            execution_time_ms=log.execution_time_ms
        )
        for log in logs
    ]


@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(days: int = Query(7, ge=1, le=365)):
    """
    Get system statistics.
    
    Args:
        days: Number of days to include in statistics (1-365)
    """
    stats = db_manager.get_statistics(days=days)
    
    return StatisticsResponse(**stats)


@app.get("/config")
async def get_config():
    """Get current configuration."""
    return {
        "observer_interval": settings.observer_interval,
        "ollama_model": settings.ollama_model,
        "ollama_temperature": settings.ollama_temperature,
        "blacklist_apps": settings.blacklist_apps,
        "whitelist_apps": settings.whitelist_apps,
        "require_confirmation_for": settings.require_confirmation_for,
        "log_level": settings.log_level
    }


@app.post("/config")
async def update_config(config: ConfigUpdateRequest):
    """
    Update configuration.
    
    Note: This only updates runtime config, not the .env file.
    """
    updated_fields = []
    
    if config.observer_interval is not None:
        settings.observer_interval = config.observer_interval
        updated_fields.append("observer_interval")
    
    if config.ollama_model is not None:
        settings.ollama_model = config.ollama_model
        updated_fields.append("ollama_model")
    
    if config.blacklist_apps is not None:
        settings.blacklist_apps = config.blacklist_apps
        updated_fields.append("blacklist_apps")
    
    logger.info(f"Configuration updated via API: {', '.join(updated_fields)}")
    
    return {
        "status": "updated",
        "updated_fields": updated_fields,
        "timestamp": datetime.now().isoformat()
    }


@app.delete("/logs/cleanup")
async def cleanup_logs(days: int = Query(30, ge=1, le=365)):
    """
    Clean up old logs.
    
    Args:
        days: Delete logs older than this many days
    """
    deleted = db_manager.cleanup_old_logs(days=days)
    
    return {
        "status": "completed",
        "deleted_count": deleted,
        "timestamp": datetime.now().isoformat()
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {
        "error": "Not Found",
        "message": f"The requested endpoint does not exist",
        "path": str(request.url)
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }
