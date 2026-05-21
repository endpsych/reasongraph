"""
Initialize Neo4j for ReasonGraph.

What this file does:
- Connects to the local Neo4j database.
- Reads neo4j/constraints.cypher.
- Executes each Cypher statement.
- Verifies that Neo4j is reachable before applying constraints.

How it fits into ReasonGraph:
- This script prepares Neo4j for idempotent reasoning graph writes.
- It should be run after starting the Neo4j Docker container.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from pathlib import Path

from reasongraph.backend.graph.neo4j_client import get_neo4j_client

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

CONSTRAINTS_PATH = Path("neo4j/constraints.cypher")


# ---------------------------------------------------------------------
# Cypher loading helpers
# ---------------------------------------------------------------------


def load_cypher_statements(path: Path) -> list[str]:
    """Load semicolon-separated Cypher statements from a file."""
    text = path.read_text(encoding="utf-8")
    statements = []

    for raw_statement in text.split(";"):
        statement = raw_statement.strip()

        if not statement:
            continue

        non_comment_lines = [
            line for line in statement.splitlines() if not line.strip().startswith("//")
        ]

        if not non_comment_lines:
            continue

        statements.append(statement)

    return statements


# ---------------------------------------------------------------------
# Initialization workflow
# ---------------------------------------------------------------------


def init_neo4j() -> None:
    """Apply ReasonGraph constraints to Neo4j."""
    if not CONSTRAINTS_PATH.exists():
        raise FileNotFoundError(f"Could not find {CONSTRAINTS_PATH}")

    statements = load_cypher_statements(CONSTRAINTS_PATH)

    client = get_neo4j_client()

    try:
        client.verify_connectivity()

        for statement in statements:
            client.execute_write(statement)

    finally:
        client.close()

    print(f"Applied {len(statements)} Neo4j constraint statements.")


# ---------------------------------------------------------------------
# Main script entry point
# ---------------------------------------------------------------------


if __name__ == "__main__":
    init_neo4j()