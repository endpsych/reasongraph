from sqlmodel import Session, select

from reasongraph.backend.db.models import Issue, Project
from reasongraph.backend.schemas.issue import IssueCreate
from reasongraph.backend.schemas.project import ProjectCreate


def create_project(session: Session, project_in: ProjectCreate) -> Project:
    project = Project(
        name=project_in.name,
        description=project_in.description,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def list_projects(session: Session) -> list[Project]:
    statement = select(Project).order_by(Project.created_at.desc())
    return list(session.exec(statement).all())


def get_project(session: Session, project_id: str) -> Project | None:
    return session.get(Project, project_id)


def create_issue_for_project(
    session: Session,
    project_id: str,
    issue_in: IssueCreate,
) -> Issue | None:
    project = get_project(session, project_id)

    if project is None:
        return None

    issue = Issue(
        project_id=project_id,
        title=issue_in.title,
        business_context=issue_in.business_context,
        decision_question=issue_in.decision_question,
        mode=issue_in.mode,
        in_scope=issue_in.in_scope,
        out_of_scope=issue_in.out_of_scope,
    )
    session.add(issue)
    session.commit()
    session.refresh(issue)
    return issue


def list_project_issues(session: Session, project_id: str) -> list[Issue] | None:
    project = get_project(session, project_id)

    if project is None:
        return None

    statement = (
        select(Issue).where(Issue.project_id == project_id).order_by(Issue.created_at.desc())
    )
    return list(session.exec(statement).all())


def get_issue(session: Session, issue_id: str) -> Issue | None:
    return session.get(Issue, issue_id)
