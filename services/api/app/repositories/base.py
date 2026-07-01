"""
Velour API — Base repository with generic CRUD operations.

Provides a reusable repository pattern for all ORM models.
All data access goes through repositories — never direct SQL in routes.
"""

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Generic repository providing standard CRUD operations.

    All queries filter out soft-deleted records by default.

    Args:
        model: The SQLAlchemy ORM model class.
        session: The async database session.
    """

    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def get_by_id(self, entity_id: uuid.UUID) -> T | None:
        """Retrieve a single entity by its UUID primary key.

        Args:
            entity_id: The UUID of the entity to retrieve.

        Returns:
            The entity if found and not soft-deleted, None otherwise.
        """
        stmt = select(self._model).where(
            self._model.id == entity_id,
            self._model.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[T]:
        """Retrieve all entities with pagination.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            A list of entities.
        """
        stmt = (
            select(self._model)
            .where(self._model.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        """Insert a new entity into the database.

        Args:
            entity: The ORM model instance to persist.

        Returns:
            The persisted entity with generated fields populated.
        """
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update_by_id(
        self,
        entity_id: uuid.UUID,
        update_data: dict[str, Any],
    ) -> T | None:
        """Update an entity by its UUID with the given data.

        Args:
            entity_id: The UUID of the entity to update.
            update_data: Dictionary of column names and new values.

        Returns:
            The updated entity if found, None otherwise.
        """
        stmt = (
            update(self._model)
            .where(
                self._model.id == entity_id,
                self._model.is_deleted.is_(False),
            )
            .values(**update_data)
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        updated = result.scalar_one_or_none()
        if updated is not None:
            await self._session.flush()
        return updated

    async def soft_delete(self, entity_id: uuid.UUID) -> bool:
        """Soft-delete an entity by setting is_deleted=True.

        Args:
            entity_id: The UUID of the entity to soft-delete.

        Returns:
            True if the entity was found and deleted, False otherwise.
        """
        from datetime import datetime, timezone

        values = {"is_deleted": True}
        if hasattr(self._model, "deleted_at"):
            values["deleted_at"] = datetime.now(timezone.utc)

        stmt = (
            update(self._model)
            .where(
                self._model.id == entity_id,
                self._model.is_deleted.is_(False),
            )
            .values(**values)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0  # type: ignore[return-value]
