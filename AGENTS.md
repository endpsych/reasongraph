# Agent Instructions for ReasonGraph

## Project identity

ReasonGraph is a business reasoning graph application.

It maps stakeholder positions, claims, assumptions, evidence, risks, criteria, options, and LLM POVs into an auditable reasoning graph.

## Development environment

Use:

- Python 3.11
- uv
- FastAPI
- SQLite
- Neo4j
- React + Vite + TypeScript
- Cytoscape.js
- pytest
- ruff

## Common commands

Install/sync dependencies:

```bash
uv sync --group dev --group notebooks