"""
Read ReasonGraph issue graphs from Neo4j.

What this file does:
- Reads the basic issue reasoning graph from Neo4j.
- Converts Neo4j nodes and relationships into Cytoscape.js-compatible JSON.
- Supports the future frontend graph visualization.

How it fits into ReasonGraph:
- Neo4j is the source of truth for explorable reasoning graphs.
- Cytoscape.js expects graph elements as nodes and edges.
- This module provides the backend translation layer.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from typing import Any

from reasongraph.backend.graph.neo4j_client import Neo4jClient

# ---------------------------------------------------------------------
# Cypher query
# ---------------------------------------------------------------------

READ_ISSUE_GRAPH_CYPHER = """
MATCH (issue:Issue {id: $issue_id})
OPTIONAL MATCH path = (issue)-[:HAS_STAKEHOLDER|HAS_POSITION|HOLDS*1..2]-(connected)
WITH issue, collect(path) AS paths
CALL {
    WITH issue, paths
    UNWIND CASE WHEN size(paths) = 0 THEN [null] ELSE paths END AS path
    WITH issue, path
    WITH
        CASE
            WHEN path IS NULL THEN [issue]
            ELSE nodes(path)
        END AS path_nodes,
        CASE
            WHEN path IS NULL THEN []
            ELSE relationships(path)
        END AS path_relationships
    RETURN
        collect(path_nodes) AS nested_nodes,
        collect(path_relationships) AS nested_relationships
}
WITH
    apoc.coll.toSet(apoc.coll.flatten(nested_nodes)) AS graph_nodes,
    apoc.coll.toSet(apoc.coll.flatten(nested_relationships)) AS graph_relationships
RETURN
    [node IN graph_nodes | {
        id: node.id,
        labels: labels(node),
        properties: properties(node)
    }] AS nodes,
    [relationship IN graph_relationships | {
        id: elementId(relationship),
        type: type(relationship),
        source: startNode(relationship).id,
        target: endNode(relationship).id,
        properties: properties(relationship)
    }] AS relationships
"""


# ---------------------------------------------------------------------
# Cytoscape conversion helpers
# ---------------------------------------------------------------------


def _node_label(labels: list[str], properties: dict[str, Any]) -> str:
    """Create a human-readable label for a Cytoscape node."""
    if "Issue" in labels:
        return str(properties.get("title", properties.get("id", "Issue")))

    if "Stakeholder" in labels:
        return str(properties.get("name", properties.get("id", "Stakeholder")))

    if "Position" in labels:
        return str(properties.get("label", properties.get("id", "Position")))

    return str(properties.get("name", properties.get("id", "Node")))


def _node_type(labels: list[str]) -> str:
    """Return the primary graph node type."""
    return labels[0] if labels else "Node"


def _to_cytoscape_node(node: dict[str, Any]) -> dict[str, Any]:
    """Convert one Neo4j node record into a Cytoscape node element."""
    labels = node["labels"]
    properties = node["properties"]

    return {
        "data": {
            "id": node["id"],
            "label": _node_label(labels=labels, properties=properties),
            "type": _node_type(labels),
            "properties": properties,
        }
    }


def _to_cytoscape_edge(relationship: dict[str, Any]) -> dict[str, Any]:
    """Convert one Neo4j relationship record into a Cytoscape edge element."""
    return {
        "data": {
            "id": relationship["id"],
            "source": relationship["source"],
            "target": relationship["target"],
            "label": relationship["type"],
            "type": relationship["type"],
            "properties": relationship["properties"],
        }
    }


# ---------------------------------------------------------------------
# Public graph read service
# ---------------------------------------------------------------------


def read_issue_graph_for_cytoscape(
    neo4j_client: Neo4jClient,
    issue_id: str,
) -> dict[str, list[dict[str, Any]]] | None:
    """
    Read an issue graph from Neo4j and return Cytoscape.js elements.

    Returns:
        {"nodes": [...], "edges": [...]} if the graph exists.
        None if the issue is not found in Neo4j.
    """
    result = neo4j_client.execute_read(
        cypher=READ_ISSUE_GRAPH_CYPHER,
        parameters={"issue_id": issue_id},
    )

    if not result:
        return None

    record = result[0]
    nodes = record.get("nodes", [])

    if not nodes:
        return None

    relationships = record.get("relationships", [])

    return {
        "nodes": [_to_cytoscape_node(node) for node in nodes],
        "edges": [
            _to_cytoscape_edge(relationship) for relationship in relationships
        ],
    }