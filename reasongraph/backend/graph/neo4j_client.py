"""
Neo4j client utilities for ReasonGraph.

What this file does:
- Creates a small wrapper around the official Neo4j Python driver.
- Provides connectivity checks.
- Provides helpers for read and write queries.
- Keeps Neo4j access centralized instead of scattering driver code across routes.

How it fits into ReasonGraph:
- Neo4j will store the auditable business reasoning graph.
- Later services will use this client to write Issues, Positions, Claims,
  Assumptions, Evidence, Risks, Criteria, Options, and LLM POVs.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from collections.abc import Mapping
from typing import Any

from neo4j import Driver, GraphDatabase
from reasongraph.backend.core.settings import Settings, get_settings

# ---------------------------------------------------------------------
# Neo4j client
# ---------------------------------------------------------------------


class Neo4jClient:
    """Small wrapper around the Neo4j Python driver."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._driver: Driver = GraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_username, self.settings.neo4j_password),
        )

    def close(self) -> None:
        """Close the underlying Neo4j driver."""
        self._driver.close()

    def verify_connectivity(self) -> None:
        """Raise an error if Neo4j is not reachable."""
        self._driver.verify_connectivity()

    def execute_write(
        self,
        cypher: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a write query and return result records as dictionaries."""
        return self._execute(cypher=cypher, parameters=parameters)

    def execute_read(
        self,
        cypher: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a read query and return result records as dictionaries."""
        return self._execute(cypher=cypher, parameters=parameters)

    def _execute(
        self,
        cypher: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query inside a managed session."""
        with self._driver.session(database=self.settings.neo4j_database) as session:
            result = session.run(cypher, dict(parameters or {}))
            return [record.data() for record in result]


# ---------------------------------------------------------------------
# Convenience helper
# ---------------------------------------------------------------------


def get_neo4j_client() -> Neo4jClient:
    """Return a new Neo4j client instance."""
    return Neo4jClient()