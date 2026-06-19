import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import (
    InvalidStatusTransitionError,
    PermissionDeniedError,
    ProjectNotFoundError,
    create_project,
    delete_project,
    get_project_for_user,
    list_projects,
    update_project,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.project import Project

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

@router.get("/", response_model=list[ProjectRead])
async def list_all(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project).options(
            selectinload(Project.owner)
        )
    )
    projects = result.scalars().all()
    return projects

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_project(db, project_in, current_user.id)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_one(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await get_project_for_user(db, project_id, current_user)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this project")


@router.patch("/{project_id}", response_model=ProjectRead)
async def update(
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await update_project(db, project_id, project_in, current_user)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to modify this project")
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {e.current.value} to {e.requested.value}",
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    try:
        await delete_project(db, project_id, current_user)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this project")