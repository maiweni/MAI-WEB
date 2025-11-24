from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas


async def list_posts(session: AsyncSession) -> list[models.Post]:
    result = await session.execute(
        select(models.Post).order_by(models.Post.created_at.desc())
    )
    return result.scalars().all()


async def get_post(session: AsyncSession, post_id: int) -> models.Post | None:
    return await session.get(models.Post, post_id)


async def get_post_by_slug(session: AsyncSession, slug: str) -> models.Post | None:
    result = await session.execute(
        select(models.Post).where(models.Post.slug == slug)
    )
    return result.scalars().first()


async def create_post(session: AsyncSession, payload: schemas.PostCreate) -> models.Post:
    tags = ",".join(payload.tags)
    post = models.Post(
        title=payload.title,
        excerpt=payload.excerpt,
        content_path=payload.content_path,
        tags=tags,
        slug=payload.slug,
        visibility=payload.visibility,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


async def update_post(
    session: AsyncSession, db_post: models.Post, payload: schemas.PostUpdate
) -> models.Post:
    data = payload.dict(exclude_unset=True)
    if "tags" in data and data["tags"] is not None:
        tags = data["tags"]
        if isinstance(tags, list):
            data["tags"] = ",".join(tags)
        elif isinstance(tags, str):
            data["tags"] = ",".join(
                [item.strip() for item in tags.split(",") if item.strip()]
            )
    for key, value in data.items():
        setattr(db_post, key, value)
    await session.commit()
    await session.refresh(db_post)
    return db_post


async def get_user_by_email(
    session: AsyncSession, email: str
) -> models.User | None:
    result = await session.execute(
        select(models.User).where(models.User.email == email)
    )
    return result.scalars().first()


async def create_user(
    session: AsyncSession, email: str, password_hash: str, role: str = "user"
) -> models.User:
    user = models.User(email=email, password_hash=password_hash, role=role)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def upgrade_membership(
    session: AsyncSession, user: models.User, expires_at
) -> models.User:
    if user.role != "admin":
        user.role = "member"
    user.membership_expires_at = expires_at
    await session.commit()
    await session.refresh(user)
    return user


async def delete_post(session: AsyncSession, db_post: models.Post) -> None:
    await session.delete(db_post)
    await session.commit()
