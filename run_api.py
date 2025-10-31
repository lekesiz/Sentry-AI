#!/usr/bin/env python3
"""
Script to run the Sentry-AI API server.

This script starts the FastAPI server that provides a REST API
for controlling and monitoring Sentry-AI.
"""

import uvicorn
from sentry_ai.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "sentry_ai.api.routes:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
