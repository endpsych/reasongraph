from fastapi import FastAPI

from reasongraph.backend.api.routes_projects import router as projects_router
from reasongraph.backend.db.init_db import init_db

app = FastAPI(
    title="ReasonGraph API",
    description=(
        "Business reasoning graph API for mapping positions, claims, "
        "assumptions, evidence, risks, and LLM POVs."
    ),
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(projects_router)
