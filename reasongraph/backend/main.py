"""
ReasonGraph FastAPI application entry point.

What this file does:
- Creates the FastAPI app.
- Initializes the SQLite metadata database on startup.
- Registers API routers for projects, issues, positions, and graph checks.

How it fits into ReasonGraph:
- This is the backend API entry point used by local development,
  future Docker services, and the future React frontend.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from fastapi import FastAPI

from reasongraph.backend.api.routes_graph import router as graph_router
from reasongraph.backend.api.routes_positions import router as positions_router
from reasongraph.backend.api.routes_projects import router as projects_router
from reasongraph.backend.api.routes_settings import router as settings_router
from reasongraph.backend.db.init_db import init_db

# ---------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------

app = FastAPI(
    title="ReasonGraph API",
    description=(
        "Business reasoning graph API for mapping positions, claims, "
        "assumptions, evidence, risks, and LLM POVs."
    ),
    version="0.1.0",
)


# ---------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------


@app.on_event("startup")
def on_startup() -> None:
    """Initialize local metadata storage when the API starts."""
    init_db()


# ---------------------------------------------------------------------
# Core routes
# ---------------------------------------------------------------------


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return backend API health status."""
    return {"status": "ok"}


# ---------------------------------------------------------------------
# Router registration
# ---------------------------------------------------------------------

app.include_router(projects_router)
app.include_router(positions_router)
app.include_router(graph_router)
app.include_router(settings_router)