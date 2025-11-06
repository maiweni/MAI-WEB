from pathlib import Path as PathlibPath

from fastapi import Depends, FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .config import settings
from .database import get_session, init_db

CONTENT_DIR = PathlibPath(__file__).resolve().parent.parent / "content"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="MAI API", version="0.1.0")

app.mount("/content", StaticFiles(directory=CONTENT_DIR), name="content")

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


@app.get("/api/posts", response_model=list[schemas.PostOut])
async def list_posts(session: AsyncSession = Depends(get_session)):
    posts = await crud.list_posts(session)
    return [schemas.PostOut.model_validate(post) for post in posts]


@app.get("/api/posts/{post_id}", response_model=schemas.PostOut)
async def get_post(
    post_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_session),
):
    db_post = await crud.get_post(session, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return schemas.PostOut.model_validate(db_post)


@app.get("/api/posts/slug/{slug}", response_model=schemas.PostDetail)
async def get_post_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
):
    db_post = await crud.get_post_by_slug(session, slug)
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return schemas.PostDetail.model_validate(db_post)
