from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.project import Project
from app.services.auth_service import hash_password


async def seed_data(db: AsyncSession):
    result = await db.execute(select(User))
    existing_users = result.scalars().all()

    if existing_users:
        return

    admin = User(
        email="admin@test.com",
        username="admin",
        hashed_password=hash_password("Admin@123"),
        role=UserRole.admin,
    )

    manager = User(
        email="manager@test.com",
        username="manager",
        hashed_password=hash_password("Manager@123"),
        role=UserRole.manager,
    )

    user = User(
        email="user@test.com",
        username="user",
        hashed_password=hash_password("User@123"),
        role=UserRole.user,
    )

    db.add_all([admin, manager, user])

    await db.flush()

    projects = [
        Project(
            title="Website Redesign",
            description="UI update",
            status="planned",
            owner_id=admin.id,
        ),
        Project(
            title="Mobile App",
            description="Flutter app",
            status="active",
            owner_id=manager.id,
        ),
        Project(
            title="CRM Migration",
            description="Move data",
            status="completed",
            owner_id=user.id,
        ),
        Project(
            title="Analytics Dashboard",
            description="Reporting",
            status="active",
            owner_id=manager.id,
        ),
        Project(
            title="API Upgrade",
            description="Version 2",
            status="planned",
            owner_id=admin.id,
        ),
    ]

    db.add_all(projects)

    await db.commit()