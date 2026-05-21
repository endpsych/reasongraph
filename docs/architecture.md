# ReasonGraph Architecture

## Purpose

ReasonGraph is a business reasoning graph application. It helps users map business issues into explicit positions, claims, assumptions, evidence, risks, criteria, options, and LLM POVs.

The MVP separates app metadata from graph reasoning data.

## Storage Architecture

ReasonGraph uses two storage layers:

1. SQLite
2. Neo4j

### SQLite

SQLite stores application metadata and raw user inputs.

Examples:

- Projects
- Issues
- Stakeholders
- Raw position input
- Extraction run metadata
- LLM POV run metadata
- Provider profile metadata
- Evaluation run metadata

SQLite is used because it is simple, local-first, easy to inspect, and suitable for the early MVP.

### Neo4j

Neo4j stores the explorable reasoning graph.

Examples:

- Issue nodes
- Stakeholder nodes
- Position nodes
- Claim nodes
- Assumption nodes
- Evidence nodes
- Risk nodes
- Decision criterion nodes
- Option nodes
- LLM POV nodes

Neo4j is used because ReasonGraph needs to represent relationships between reasoning objects in an auditable and explorable way.

## Current Graph Sync Flow

The current MVP sync flow is:

```text
SQLite Issue + Stakeholders + PositionInput records
→ sync_issue_graph_to_neo4j()
→ Neo4j Issue, Stakeholder, and Position nodes
→ read_issue_graph_for_cytoscape()
→ Cytoscape.js-compatible JSON