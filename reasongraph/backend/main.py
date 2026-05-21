from fastapi import FastAPI

app = FastAPI(
    title="ReasonGraph API",
    description=(
        "Business reasoning graph API for mapping positions, claims, "
        "assumptions, evidence, risks, and LLM POVs."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}