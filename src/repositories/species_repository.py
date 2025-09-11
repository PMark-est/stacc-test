from typing import Optional, List
from sqlalchemy import select, func
from src.models import Species
from src.repositories.base_repository import BaseRepository


class SpeciesRepository(BaseRepository):
    """
    Repository for Species CRUD operations.
    """

    def get_all(self) -> List[Species]:
        """Return all Species ordered by id."""
        stmt = select(Species).order_by(Species.id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_name(self, name: str) -> Optional[Species]:
        """Return a species by name (case-insensitive) or None."""
        return self.session.execute(select(Species).where(func.lower(Species.name) == name.lower())).scalar_one_or_none()
