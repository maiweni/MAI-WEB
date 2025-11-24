from datetime import datetime, timedelta, timezone
from pathlib import Path as PathlibPath

from fastapi import Depends, FastAPI, HTTPException, Path, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .config import settings
from .database import get_session, init_db
from .security import (
    create_access_token,
    decode_token,
    get_token_from_credentials,
    hash_password,
    security_scheme,
    verify_password,
)

CONTENT_DIR = PathlibPath(__file__).resolve().parent.parent / "content"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="MAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session),
) -> models.User:
    token = get_token_from_credentials(credentials)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="需要登录后才能查看内容"
        )
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="凭证无效"
        )
    user = await session.get(models.User, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已被移除"
        )
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_session),
) -> models.User | None:
    token = get_token_from_credentials(credentials)
    if not token:
        return None
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = await session.get(models.User, int(user_id))
    return user


def is_membership_active(user: models.User) -> bool:
    if user.role in {"admin"}:
        return True
    if user.role != "member":
        return False
    if user.membership_expires_at is None:
        return True
    return user.membership_expires_at > datetime.now(timezone.utc)


def read_markdown_content(content_path: str) -> str:
    path = PathlibPath(content_path)
    if not path.is_absolute():
        path = CONTENT_DIR / content_path
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="文章正文不存在"
        )
    return path.read_text(encoding="utf-8")


@app.post("/api/auth/register")
async def register(
    payload: schemas.UserCreate, session: AsyncSession = Depends(get_session)
):
    existing = await crud.get_user_by_email(session, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    user = await crud.create_user(
        session=session,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="user",
    )
    token = create_access_token(
        subject=str(user.id), expires_minutes=settings.access_token_expire_minutes
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": schemas.UserOut.model_validate(user),
    }


@app.post("/api/auth/login")
async def login(
    payload: schemas.UserLogin, session: AsyncSession = Depends(get_session)
):
    user = await crud.get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(
        subject=str(user.id), expires_minutes=settings.access_token_expire_minutes
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": schemas.UserOut.model_validate(user),
    }


@app.get("/api/auth/me", response_model=schemas.UserOut)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserOut.model_validate(current_user)


@app.post("/api/auth/upgrade", response_model=schemas.UserOut)
async def upgrade_membership(
    current_user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    updated = await crud.upgrade_membership(session, current_user, expires_at)
    return schemas.UserOut.model_validate(updated)


@app.get("/api/posts", response_model=list[schemas.PostOut])
async def list_posts(session: AsyncSession = Depends(get_session)):
    posts = await crud.list_posts(session)
    return [schemas.PostOut.model_validate(post) for post in posts]


@app.get("/api/posts/{post_id}", response_model=schemas.PostDetail)
async def get_post(
    post_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: models.User | None = Depends(get_optional_user),
):
    db_post = await crud.get_post(session, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="需要登录后才能查看全文"
        )
    if db_post.visibility == "member" and not is_membership_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="会员可查看，升级后继续阅读",
        )
    content = read_markdown_content(db_post.content_path)
    payload = schemas.PostDetail.model_validate(db_post)
    payload.content = content
    return payload


@app.get("/api/posts/slug/{slug}", response_model=schemas.PostDetail)
async def get_post_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
    current_user: models.User | None = Depends(get_optional_user),
):
    db_post = await crud.get_post_by_slug(session, slug)
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="需要登录后才能查看全文"
        )
    if db_post.visibility == "member" and not is_membership_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="会员可查看，升级后继续阅读",
        )
    content = read_markdown_content(db_post.content_path)
    payload = schemas.PostDetail.model_validate(db_post)
    payload.content = content
    return payload
