"""
Tests for ReasonGraph Neo4j-to-Cytoscape graph read helpers.

What this file does:
- Tests conversion of Neo4j-style node and relationship dictionaries into
  Cytoscape.js-compatible elements.
- Verifies node labels, node types, edge labels, and edge endpoints.
- Avoids requiring a live Neo4j database.

How it fits into ReasonGraph:
- The React frontend will use Cytoscape.js for graph visualization.
- These tests protect the backend response format expected by the frontend.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from reasongraph.backend.graph.read_graph import (
    _node_label,
    _node_type,
    _to_cytoscape_edge,
    _to_cytoscape_node,
)

# ---------------------------------------------------------------------
# Node label tests
# ---------------------------------------------------------------------


def test_node_label_for_issue() -> None:
    """Issue nodes should use the issue title as the display label."""
    label = _node_label(
        labels=["Issue"],
        properties={
            "id": "issue_test",
            "title": "AI provider selection",
        },
    )

    assert label == "AI provider selection"


def test_node_label_for_stakeholder() -> None:
    """Stakeholder nodes should use the stakeholder name as the display label."""
    label = _node_label(
        labels=["Stakeholder"],
        properties={
            "id": "stakeholder_test",
            "name": "CTO",
        },
    )

    assert label == "CTO"


def test_node_label_for_position() -> None:
    """Position nodes should use the position label as the display label."""
    label = _node_label(
        labels=["Position"],
        properties={
            "id": "position_test",
            "label": "Use OpenAI for the first MVP",
        },
    )

    assert label == "Use OpenAI for the first MVP"


def test_node_type_uses_first_label() -> None:
    """Node type should use the first Neo4j label."""
    assert _node_type(["Position"]) == "Position"


def test_node_type_fallback() -> None:
    """Node type should fall back to Node if no labels exist."""
    assert _node_type([]) == "Node"


# ---------------------------------------------------------------------
# Cytoscape node conversion tests
# ---------------------------------------------------------------------


def test_to_cytoscape_node() -> None:
    """Neo4j node dictionaries should convert to Cytoscape node elements."""
    node = {
        "id": "position_test",
        "labels": ["Position"],
        "properties": {
            "id": "position_test",
            "label": "Use OpenAI for the first MVP",
            "confidence": 0.78,
        },
    }

    cytoscape_node = _to_cytoscape_node(node)

    assert cytoscape_node == {
        "data": {
            "id": "position_test",
            "label": "Use OpenAI for the first MVP",
            "type": "Position",
            "properties": {
                "id": "position_test",
                "label": "Use OpenAI for the first MVP",
                "confidence": 0.78,
            },
        }
    }


# ---------------------------------------------------------------------
# Cytoscape edge conversion tests
# ---------------------------------------------------------------------


def test_to_cytoscape_edge() -> None:
    """Neo4j relationship dictionaries should convert to Cytoscape edge elements."""
    relationship = {
        "id": "rel_test",
        "type": "HAS_POSITION",
        "source": "issue_test",
        "target": "position_test",
        "properties": {},
    }

    cytoscape_edge = _to_cytoscape_edge(relationship)

    assert cytoscape_edge == {
        "data": {
            "id": "rel_test",
            "source": "issue_test",
            "target": "position_test",
            "label": "HAS_POSITION",
            "type": "HAS_POSITION",
            "properties": {},
        }
    }