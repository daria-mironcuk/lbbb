from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.post import Post


class CRUDPost(CRUDBase[Post]):
    async def get_by_author(
        self,
        db: AsyncSession,
        author_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Post]:
        """Повертає пости конкретного автора."""
        result = await db.execute(
            select(Post)
            .where(Post.author_id == author_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[Post]:
        """Повертає пост за унікальним slug."""
        result = await db.execute(select(Post).where(Post.slug == slug))
        return result.scalar_one_or_none()


crud_post = CRUDPost(Post)