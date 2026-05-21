"""
Seed ReasonGraph example business cases into SQLite.

What this file does:
- Reads JSON example files from data/examples/.
- Creates or reuses the shared example Project.
- Creates or reuses Issues for each business case.
- Creates or reuses Stakeholders for each issue.
- Creates PositionInput records for each stakeholder position.
- Keeps the operation mostly idempotent so the script can be run multiple times.

How it fits into ReasonGraph:
- This script provides realistic test data for the project dashboard,
  issue setup, stakeholder input, and later graph extraction workflows.
- It writes only to SQLite metadata storage.
- It does not write to Neo4j yet.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import json
from pathlib import Path
from typing import Any

from sqlmodel import Session, select

from reasongraph.backend.db.init_db import init_db
from reasongraph.backend.db.models import Issue, PositionInput, Project, Stakeholder
from reasongraph.backend.db.session import engine

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

EXAMPLES_DIR = Path("data/examples")


# ---------------------------------------------------------------------
# File loading helpers
# ---------------------------------------------------------------------


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file as a dictionary."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------------------
# Project seeding helpers
# ---------------------------------------------------------------------


def get_or_create_project(session: Session, project_data: dict[str, Any]) -> Project:
    """Return an existing project by name, or create it if it does not exist."""
    statement = select(Project).where(Project.name == project_data["name"])
    existing_project = session.exec(statement).first()

    if existing_project is not None:
        return existing_project

    project = Project(
        name=project_data["name"],
        description=project_data.get("description", ""),
    )
    session.add(project)
    session.commit()
    session.refresh(project)

    return project


# ---------------------------------------------------------------------
# Issue seeding helpers
# ---------------------------------------------------------------------


def get_or_create_issue(
    session: Session,
    project: Project,
    issue_data: dict[str, Any],
) -> Issue:
    """Return an existing issue by project and title, or create it."""
    statement = (
        select(Issue)
        .where(Issue.project_id == project.id)
        .where(Issue.title == issue_data["title"])
    )
    existing_issue = session.exec(statement).first()

    if existing_issue is not None:
        return existing_issue

    issue = Issue(
        project_id=project.id,
        title=issue_data["title"],
        business_context=issue_data.get("business_context", ""),
        decision_question=issue_data.get("decision_question", ""),
        mode=issue_data.get("mode", "reasoning_analysis"),
        in_scope=issue_data.get("in_scope", ""),
        out_of_scope=issue_data.get("out_of_scope", ""),
    )
    session.add(issue)
    session.commit()
    session.refresh(issue)

    return issue


# ---------------------------------------------------------------------
# Stakeholder seeding helpers
# ---------------------------------------------------------------------


def get_or_create_stakeholders(
    session: Session,
    issue: Issue,
    stakeholder_data: list[dict[str, Any]],
) -> dict[str, Stakeholder]:
    """Return stakeholders keyed by name, creating missing ones."""
    stakeholders_by_name: dict[str, Stakeholder] = {}

    for item in stakeholder_data:
        statement = (
            select(Stakeholder)
            .where(Stakeholder.issue_id == issue.id)
            .where(Stakeholder.name == item["name"])
        )
        existing_stakeholder = session.exec(statement).first()

        if existing_stakeholder is not None:
            stakeholders_by_name[existing_stakeholder.name] = existing_stakeholder
            continue

        stakeholder = Stakeholder(
            issue_id=issue.id,
            name=item["name"],
            role=item.get("role", ""),
            organization_unit=item.get("organization_unit", ""),
        )
        session.add(stakeholder)
        session.commit()
        session.refresh(stakeholder)

        stakeholders_by_name[stakeholder.name] = stakeholder

    return stakeholders_by_name


# ---------------------------------------------------------------------
# Position seeding helpers
# ---------------------------------------------------------------------


def create_missing_positions(
    session: Session,
    issue: Issue,
    stakeholders_by_name: dict[str, Stakeholder],
    position_data: list[dict[str, Any]],
) -> int:
    """Create missing positions for an issue and return the number created."""
    created_count = 0

    for item in position_data:
        stakeholder_name = item.get("stakeholder_name")
        stakeholder = stakeholders_by_name.get(stakeholder_name) if stakeholder_name else None

        statement = (
            select(PositionInput)
            .where(PositionInput.issue_id == issue.id)
            .where(PositionInput.label == item["label"])
        )
        existing_position = session.exec(statement).first()

        if existing_position is not None:
            continue

        position = PositionInput(
            issue_id=issue.id,
            stakeholder_id=stakeholder.id if stakeholder is not None else None,
            label=item["label"],
            recommendation=item.get("recommendation", ""),
            reasoning_text=item["reasoning_text"],
            claims_text=item.get("claims_text", ""),
            assumptions_text=item.get("assumptions_text", ""),
            evidence_text=item.get("evidence_text", ""),
            criteria_text=item.get("criteria_text", ""),
            risks_text=item.get("risks_text", ""),
            confidence=item.get("confidence"),
            would_change_mind=item.get("would_change_mind", ""),
        )
        session.add(position)
        created_count += 1

    session.commit()
    return created_count


# ---------------------------------------------------------------------
# Example seeding workflow
# ---------------------------------------------------------------------


def seed_example(path: Path) -> None:
    """Seed one example JSON file into SQLite."""
    example = load_json(path)

    with Session(engine) as session:
        project = get_or_create_project(session, example["project"])
        issue = get_or_create_issue(session, project, example["issue"])

        stakeholders_by_name = get_or_create_stakeholders(
            session=session,
            issue=issue,
            stakeholder_data=example.get("stakeholders", []),
        )

        created_positions = create_missing_positions(
            session=session,
            issue=issue,
            stakeholders_by_name=stakeholders_by_name,
            position_data=example.get("positions", []),
        )

    print(f"Seeded {path.name}: created {created_positions} new positions.")


# ---------------------------------------------------------------------
# Main script entry point
# ---------------------------------------------------------------------


def main() -> None:
    """Initialize the database and seed all example files."""
    init_db()

    example_files = sorted(EXAMPLES_DIR.glob("*.json"))

    if not example_files:
        raise FileNotFoundError(f"No JSON examples found in {EXAMPLES_DIR}")

    for path in example_files:
        seed_example(path)

    print("Seed examples loaded successfully.")


if __name__ == "__main__":
    main()