# ReasonGraph Project Context

## Project purpose

ReasonGraph is a business reasoning graph application for making stakeholder reasoning explicit, explorable, and auditable.

The app helps users structure business disagreements and decision issues by mapping positions, claims, assumptions, evidence, risks, criteria, options, and LLM-generated points of view.

The project is not a personal conflict, mental health, or emotional analysis tool. The MVP is focused only on business applications.

## MVP scope

The MVP supports two modes:

### 1. Reasoning Analysis Mode

A single user analyzes multiple positions on a business issue.

Example:

- Position 1: Raise prices to protect margins.
- Position 2: Avoid raising prices because churn risk is too high.
- Position 3: Use segmented pricing.

### 2. Disagreement Structuring Mode

Two or more stakeholders structure their logic around an issue in a comparable and auditable way.

A stakeholder can request that another stakeholder explain their logic clearly by documenting their position, claims, assumptions, evidence, risks, criteria, and confidence.

## Core business cases

The initial MVP should support these cases:

1. Pricing strategy
2. Vendor selection
3. AI provider selection

## Core terminology

Use **position**, not **side**.

The product models disagreement as conflict between belief structures, reasoning chains, criteria, and assumptions, not as conflict between people.

Important objects:

- Project
- Issue
- Stakeholder
- Position
- Claim
- Assumption
- Evidence
- Concept
- Decision criterion
- Option
- Risk
- Question
- LLM POV
- Analysis run
- Evaluation run

## LLM POV

The app should use the term **LLM POV**, not judge, arbiter, verdict, or final decision.

An LLM POV is a model-generated interpretation of the reasoning graph. It should include model/provider metadata and should not be presented as objective truth.

## Technology choices

Backend:

- Python 3.11
- FastAPI
- Pydantic
- SQLModel / SQLAlchemy
- SQLite for app metadata
- Neo4j for reasoning graph data
- LangGraph for reasoning workflows
- OpenAI provider integration for the MVP

Frontend:

- React
- Vite
- TypeScript
- Cytoscape.js for graph visualization

Development:

- uv for dependency management
- Docker Compose for local services
- GitHub for version control
- pytest for testing
- ruff for linting and formatting
- MIT license

## Storage responsibilities

SQLite stores:

- projects
- issues
- raw position inputs
- provider/model configuration metadata
- LLM run metadata
- extraction run metadata
- evaluation run metadata

Neo4j stores:

- issue graph
- positions
- stakeholders
- claims
- assumptions
- evidence
- risks
- criteria
- options
- concepts
- LLM POV nodes

## API key policy

API keys must never be committed, logged, or stored in plaintext.

The app should support:

1. Session-only API keys
2. Encrypted local key vault storage
3. Complete key deletion from the UI

The preferred local key vault implementation is Python `keyring`.

## Initial development priority

The central product loop is:

1. Create project
2. Create issue
3. Add positions and stakeholder reasoning
4. Extract structured reasoning with LLM
5. Review extraction before saving
6. Write approved graph to Neo4j
7. Visualize graph with Cytoscape.js
8. Generate LLM POV
9. Evaluate reasoning quality