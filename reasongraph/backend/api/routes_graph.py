"""
Graph API routes for ReasonGraph.

What this file does:
- Exposes API endpoints related to the Neo4j graph backend.
- Provides a health check for the Neo4j connection.
- Syncs SQLite issue metadata into Neo4j.
- Reads issue graphs from Neo4j in Cytoscape.js format.

How it fits into ReasonGraph:
- The frontend will call these endpoints to write and visualize reasoning graphs.
- Neo4j is used for graph exploration, while SQLite stores app metadata.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from typing import Any

from fastapi import APIRouter, HTTPException

from reasongraph.backend.db.session import get_session
from reasongraph.backend.graph.neo4j_client import get_neo4j_client
from reasongraph.backend.graph.read_graph import read_issue_graph_for_cytoscape
from reasongraph.backend.graph.write_graph import sync_issue_graph_to_neo4j

# ---------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------

router = APIRouter(tags=["graph"])


# ---------------------------------------------------------------------
# Health route
# ---------------------------------------------------------------------


@router.get("/graph/health")
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


# ---------------------------------------------------------------------
# Issue graph routes
# ---------------------------------------------------------------------


@router.post("/issues/{issue_id}/graph/sync")
def sync_issue_graph_route(issue_id: str) -> dict[str, object]:
    """Sync one SQLite issue and its positions into Neo4j."""
    client = get_neo4j_client()

    try:
        with get_session() as session:
            result = sync_issue_graph_to_neo4j(
                session=session,
                neo4j_client=client,
                issue_id=issue_id,
            )

        if result is None:
            raise HTTPException(status_code=404, detail="Issue not found in SQLite")

        return result

    finally:
        client.close()


@router.get("/issues/{issue_id}/graph")
def read_issue_graph_route(issue_id: str) -> dict[str, list[dict[str, Any]]]:
    """Read one issue graph from Neo4j in Cytoscape.js format."""
    client = get_neo4j_client()

    try:
        graph = read_issue_graph_for_cytoscape(
            neo4j_client=client,
            issue_id=issue_id,
        )

        if graph is None:
            raise HTTPException(status_code=404, detail="Issue graph not found in Neo4j")

        return graph

    finally:
        client.close()