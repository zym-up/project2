"""FastAPI application entry point."""
import json
import logging
from pathlib import Path

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.routers import config, projects, analysis, reports

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

app = FastAPI(
    title="DS Agent v2",
    version="2.0.0",
    description="LangChain + LangGraph Data Scientist Agent",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config.router)
app.include_router(projects.router)
app.include_router(analysis.router)
app.include_router(reports.router)


@app.exception_handler(Exception)
async def global_handler(request, exc):
    logging.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


# Serve frontend static files in production
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
