"""
ReasonGraph backend settings.

What this file does:
- Defines typed application settings for local development.
- Loads values from environment variables and .env files.
- Centralizes SQLite and Neo4j connection configuration.

How it fits into ReasonGraph:
- The backend should not hardcode database credentials or file paths.
- Services such as the SQLite session manager and Neo4j client read
  configuration from this module.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------
# Application settings
# ---------------------------------------------------------------------


class Settings(BaseSettings):
    """Typed configuration for the ReasonGraph backend."""

    sqlite_path: str = Field(
        default="data/app/reasongraph.db",
        alias="REASONGRAPH_SQLITE_PATH",
    )

    neo4j_uri: str = Field(
        default="bolt://localhost:7687",
        alias="REASONGRAPH_NEO4J_URI",
    )
    neo4j_username: str = Field(
        default="neo4j",
        alias="REASONGRAPH_NEO4J_USERNAME",
    )
    neo4j_password: str = Field(
        default="change_me",
        alias="REASONGRAPH_NEO4J_PASSWORD",
    )
    neo4j_database: str = Field(
        default="neo4j",
        alias="REASONGRAPH_NEO4J_DATABASE",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# ---------------------------------------------------------------------
# Cached settings accessor
# ---------------------------------------------------------------------


@lru_cache
def get_settings() -> Settings:
    """Return cached backend settings."""
    return Settings()