from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models import Species
from typing import Optional, List
from src.repositories.base_repository import BaseRepository


class SpeciesRepository(BaseRepository):
    """
    A repository class for handling database operations for Species entities.

    This class encapsulates all SQLAlchemy queries related to the Species model,
    providing a clean interface for the service layer to interact with species data.

    Attributes:
        db (Session): The SQLAlchemy database session used for all operations.
    """

    def get_count(self) -> int:
        """
        Retrieves the total count of all species in the database.

        Returns:
            int: The total number of species records.
        """
        return self.session.query(Species).count()

    def get_all(self) -> List[Species]:
        """
        Retrieves all Species entities from the database.

        Returns:
            List[Species]: A list of all Species objects, ordered by ID.
        """
        stmt = select(Species).order_by(Species.id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def _get_by_name(self, name: str) -> Optional[Species]:
        """
        Retrieves a single Species entity by its unique name.

        Args:
            name (str): The unique name of the species to retrieve.

        Returns:
            Optional[Species]: The Species object if found, otherwise None.
        """
        # db.get() uses the primary key, so we need to query by name instead
        return self.session.query(Species).filter(Species.name == name).first()

    def create(self, name: str) -> Species:
        """
        Creates a new Species entity with the given name.

        Args:
            name (str): The name for the new species.

        Returns:
            Species: The newly created Species object.

        Raises:
            ValueError: If a species with the given name already exists.
        """
        # Check if species already exists
        if self._get_by_name(name):
            raise ValueError(f"Species with name '{name}' already exists")

        new_species = Species(name=name)
        self.session.add(new_species)
        self.session.commit()
        self.session.refresh(new_species)
        return new_species
