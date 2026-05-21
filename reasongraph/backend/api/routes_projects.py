from fastapi import APIRouter, HTTPException

from reasongraph.backend.db.session import get_session
from reasongraph.backend.schemas.issue import IssueCreate, IssueRead
from reasongraph.backend.schemas.project import ProjectCreate, ProjectRead
from reasongraph.backend.services.project_service import (
    create_issue_for_project,
    create_project,
    get_issue,
    get_project,
    list_project_issues,
    list_projects,
)

router = APIRouter(tags=["projects"])


@router.post("/projects", response_model=ProjectRead, status_code=201)
def create_project_route(project_in: ProjectCreate) -> ProjectRead:
    with get_session() as session:
        project = create_project(session, project_in)
        return ProjectRead.model_validate(project)


@router.get("/projects", response_model=list[ProjectRead])
def list_projects_route() -> list[ProjectRead]:
    with get_session() as session:
        projects = list_projects(session)
        return [ProjectRead.model_validate(project) for project in projects]


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project_route(project_id: str) -> ProjectRead:
    with get_session() as session:
        project = get_project(session, project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        return ProjectRead.model_validate(project)


@router.post("/projects/{project_id}/issues", response_model=IssueRead, status_code=201)
def create_issue_route(project_id: str, issue_in: IssueCreate) -> IssueRead:
    with get_session() as session:
        issue = create_issue_for_project(session, project_id, issue_in)

        if issue is None:
            raise HTTPException(status_code=404, detail="Project not found")

        return IssueRead.model_validate(issue)


@router.get("/projects/{project_id}/issues", response_model=list[IssueRead])
def list_project_issues_route(project_id: str) -> list[IssueRead]:
    with get_session() as session:
        issues = list_project_issues(session, project_id)

        if issues is None:
            raise HTTPException(status_code=404, detail="Project not found")

        return [IssueRead.model_validate(issue) for issue in issues]


@router.get("/issues/{issue_id}", response_model=IssueRead, tags=["issues"])
def get_issue_route(issue_id: str) -> IssueRead:
    with get_session() as session:
        issue = get_issue(session, issue_id)

        if issue is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        return IssueRead.model_validate(issue)
