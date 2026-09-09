from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse, PostUpdate

router = APIRouter()


async def _get_post_or_404(post_id: int, db: AsyncSession) -> Post:
    post = await db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    db: AsyncSession = Depends(get_db),
) -> Post:
    user = await db.get(User, post_data.owner_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    post = Post(**post_data.model_dump())
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.get("/", response_model=list[PostResponse])
async def get_posts(db: AsyncSession = Depends(get_db)) -> list[Post]:
    result = await db.execute(select(Post).order_by(Post.id))
    return list(result.scalars().all())


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)) -> Post:
    return await _get_post_or_404(post_id, db)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: AsyncSession = Depends(get_db),
) -> Post:
    post = await _get_post_or_404(post_id, db)

    for field, value in post_data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)) -> None:
    post = await _get_post_or_404(post_id, db)
    await db.delete(post)
    await db.commit()