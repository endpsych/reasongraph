"""
Graph API routes for ReasonGraph.

What this file does:
- Exposes API endpoints related to the Neo4j graph backend.
- Provides a health check for the Neo4j connection.

How it fits into ReasonGraph:
- This route module lets the backend verify that Neo4j is reachable.
- Later, this module will expose issue graph reads for Cytoscape.js.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException

from reasongraph.backend.graph.neo4j_client import get_neo4j_client

# ---------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------

router = APIRouter(prefix="/graph", tags=["graph"])


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------


@router.get("/health")
def graph_health_check() -> dict[str, str]:
    """Check whether Neo4j is reachable."""
    client = get_neo4j_client()

    try:
        client.verify_connectivity()
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Neo4j is not reachable: {error}",
        ) from error
    finally:
        client.close()

    return {"status": "ok"}