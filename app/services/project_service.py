import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate

ALLOWED_TRANSITIONS: dict[ProjectStatus, set[ProjectStatus]] = {
    ProjectStatus.draft: {ProjectStatus.active},
    ProjectStatus.active: {ProjectStatus.completed, ProjectStatus.archived},
    ProjectStatus.completed: {ProjectStatus.archived},
    ProjectStatus.archived: set(),
}


class ProjectNotFoundError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    def __init__(self, current: ProjectStatus, requested: ProjectStatus):
        self.current = current
        self.requested = requested
        super().__init__(f"Cannot transition from {current.value} to {requested.value}")


async def create_project(
    db: AsyncSession, project_in: ProjectCreate, owner_id: uuid.UUID
) -> Project:
    project = Project(
        title=project_in.title,
        description=project_in.description,
        owner_id=owner_id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise ProjectNotFoundError(project_id)
    return project


async def list_projects(db: AsyncSession, current_user: User) -> list[Project]:
    query = select(Project)
    if current_user.role == UserRole.user:
        query = query.where(Project.owner_id == current_user.id)
    result = await db.execute(query)
    return list(result.scalars().all())


def _ensure_can_modify(project: Project, current_user: User) -> None:
    if current_user.role in (UserRole.admin, UserRole.manager):
        return
    if project.owner_id != current_user.id:
        raise PermissionDeniedError(project.id)


async def update_project(
    db: AsyncSession,
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    current_user: User,
) -> Project:
    project = await get_project(db, project_id)
    _ensure_can_modify(project, current_user)

    if project_in.status is not None and project_in.status != project.status:
        if project_in.status not in ALLOWED_TRANSITIONS[project.status]:
            raise InvalidStatusTransitionError(project.status, project_in.status)
        project.status = project_in.status

    if project_in.title is not None:
        project.title = project_in.title
    if project_in.description is not None:
        project.description = project_in.description

    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(
    db: AsyncSession, project_id: uuid.UUID, current_user: User
) -> None:
    project = await get_project(db, project_id)
    if current_user.role != UserRole.admin:
        raise PermissionDeniedError(project_id)
    await db.delete(project)
    await db.commit()

from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def get_project_for_user(
    db: AsyncSession,
    project_id: uuid.UUID,
    current_user: User,
):
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.owner)
        )
        .where(Project.id == project_id)
    )

    project = result.scalar_one_or_none()

    if project is None:
        raise ProjectNotFoundError()

    if (
        current_user.role != UserRole.admin
        and project.owner_id != current_user.id
    ):
        raise PermissionDeniedError()

    return project