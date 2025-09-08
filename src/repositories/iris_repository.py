from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from typing import List
from src.models import Species, Iris


class IrisRepository:
    """
    A repository class for handling database operations for Iris entities.

    This class encapsulates all SQLAlchemy queries related to the Iris model,
    providing methods to retrieve iris measurements filtered by species and
    sorted by various attributes.

    Attributes:
        db (Session): The SQLAlchemy database session used for all operations.
    """

    def __init__(self, db: Session):
        """
        Initializes the IrisRepository with a database session.

        Args:
            db (Session): The SQLAlchemy database session instance.
        """
        self.db = db

    def _get_iris_by_species_name(self, name: str, order: str, sort_column) -> List[Iris]:
        """
        Private helper method to retrieve iris data by species name with sorting.

        Args:
            name (str): The name of the species to filter by.
            order (str): The sort order, must be 'asc' or 'desc'.
            sort_column: The Iris attribute to sort by.

        Returns:
            List[Iris]: List of Iris entities matching the criteria.

        Raises:
            ValueError: If an invalid sort order is provided.
        """
        if order.lower() not in ('asc', 'desc'):
            raise ValueError("Order must be 'asc' or 'desc'")

        stmt = select(Iris).join(Iris.species).filter(Species.name == name)

        if order.lower() == 'asc':
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_petal_width_by_name(self, name: str, order: str = 'asc') -> List[Iris]:
        """
        Retrieves all Iris records for a given species name, sorted by petal width.

        Args:
            name (str): The name of the species to filter by (e.g., 'setosa', 'versicolor').
            order (str): The sort order for petal width. Must be 'asc' or 'desc'.
                        Defaults to 'asc'.

        Returns:
            List[Iris]: A list of Iris entities for the specified species,
                        sorted by petal width.

        Example:
            >>> repo.get_petal_width_by_name('setosa', 'desc')
            [<Iris petal_width=0.6>, <Iris petal_width=0.5>, ...]
        """
        return self._get_iris_by_species_name(name, order, Iris.petal_width)

    def get_petal_length_by_name(self, name: str, order: str = 'asc') -> List[Iris]:
        """
        Retrieves all Iris records for a given species name, sorted by petal length.

        Args:
            name (str): The name of the species to filter by (e.g., 'setosa', 'versicolor').
            order (str): The sort order for petal length. Must be 'asc' or 'desc'.
                        Defaults to 'asc'.

        Returns:
            List[Iris]: A list of Iris entities for the specified species,
                        sorted by petal length.

        Example:
            >>> repo.get_petal_length_by_name('virginica', 'asc')
            [<Iris petal_length=4.5>, <Iris petal_length=4.8>, ...]
        """
        return self._get_iris_by_species_name(name, order, Iris.petal_length)

    def get_sepal_width_by_name(self, name: str, order: str = 'asc') -> List[Iris]:
        """
        Retrieves all Iris records for a given species name, sorted by sepal width.

        Args:
            name (str): The name of the species to filter by (e.g., 'setosa', 'versicolor').
            order (str): The sort order for sepal width. Must be 'asc' or 'desc'.
                        Defaults to 'asc'.

        Returns:
            List[Iris]: A list of Iris entities for the specified species,
                        sorted by sepal width.

        Example:
            >>> repo.get_sepal_width_by_name('versicolor', 'desc')
            [<Iris sepal_width=3.3>, <Iris sepal_width=3.2>, ...]
        """
        return self._get_iris_by_species_name(name, order, Iris.sepal_width)

    def get_sepal_length_by_name(self, name: str, order: str = 'asc') -> List[Iris]:
        """
        Retrieves all Iris records for a given species name, sorted by sepal length.

        Args:
            name (str): The name of the species to filter by (e.g., 'setosa', 'versicolor').
            order (str): The sort order for sepal length. Must be 'asc' or 'desc'.
                        Defaults to 'asc'.

        Returns:
            List[Iris]: A list of Iris entities for the specified species,
                        sorted by sepal length.

        Example:
            >>> repo.get_sepal_length_by_name('setosa', 'asc')
            [<Iris sepal_length=4.3>, <Iris sepal_length=4.4>, ...]
        """
        return self._get_iris_by_species_name(name, order, Iris.sepal_length)

    def get_all_by_species_name(self, name: str) -> List[Iris]:
        """
        Retrieves all Iris records for a given species name without any sorting.

        Args:
            name (str): The name of the species to filter by.

        Returns:
            List[Iris]: A list of all Iris entities for the specified species.

        Example:
            >>> repo.get_all_by_species_name('setosa')
            [<Iris id=1>, <Iris id=2>, ...]
        """
        stmt = select(Iris).join(Iris.species).filter(Species.name == name)
        result = self.db.execute(stmt)
        return list(result.scalars().all())
