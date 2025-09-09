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

        Example:
            >>> repo.get_count()
            3
        """
        return self.session.query(Species).count()

    def get_all(self) -> List[Species]:
        """
        Retrieves all Species entities from the database.

        Returns:
            List[Species]: A list of all Species objects, ordered by ID.

        Example:
            >>> repo.get_all()
            [<Species id=1, name='setosa'>, <Species id=2, name='versicolor'>, ...]
        """
        stmt = select(Species).order_by(Species.id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_name(self, name: str) -> Optional[Species]:
        """
        Retrieves a single Species entity by its unique name.

        Args:
            name (str): The unique name of the species to retrieve.

        Returns:
            Optional[Species]: The Species object if found, otherwise None.

        Example:
            >>> repo.get_by_name('setosa')
            <Species id=1, name='setosa'>
        """
        # db.get() uses the primary key, so we need to query by name instead
        return self.session.query(Species).filter(Species.name == name).first()

    def get_by_id(self, species_id: int) -> Optional[Species]:
        """
        Retrieves a single Species entity by its unique integer ID.

        Args:
            species_id (int): The unique primary key ID of the species to retrieve.

        Returns:
            Optional[Species]: The Species object if found, otherwise None.

        Example:
            >>> repo.get_by_id(1)
            <Species id=1, name='setosa'>
        """
        return self.session.get(Species, species_id)

    def create(self, name: str) -> Species:
        """
        Creates a new Species entity with the given name.

        Args:
            name (str): The name for the new species.

        Returns:
            Species: The newly created Species object.

        Raises:
            ValueError: If a species with the given name already exists.

        Example:
            >>> repo.create('new_species')
            <Species id=4, name='new_species'>
        """
        # Check if species already exists
        if self.get_by_name(name):
            raise ValueError(f"Species with name '{name}' already exists")

        new_species = Species(name=name)
        self.session.add(new_species)
        self.session.commit()
        self.session.refresh(new_species)
        return new_species

    def delete_by_id(self, species_id: int) -> bool:
        """
        Deletes a Species entity by its ID.

        Args:
            species_id (int): The ID of the species to delete.

        Returns:
            bool: True if the species was found and deleted, False otherwise.

        Example:
            >>> repo.delete_by_id(4)
            True
        """
        species = self.get_by_id(species_id)
        if species:
            self.session.delete(species)
            self.session.commit()
            return True
        return False
