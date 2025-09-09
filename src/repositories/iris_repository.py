from sqlalchemy import select, asc, desc, func
from typing import List, Optional
from src.models import Species, Iris
from src.repositories.base_repository import BaseRepository
import numpy as np


class IrisRepository(BaseRepository):
    """
    Repository class for handling database operations for Iris entities.
    """

    def _query_by_column(
        self,
        column,
        operator: str,
        value,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        species: Optional[str] = None
    ) -> List[Iris]:
        """
        Generic helper to query Iris by column with a comparison operator.

        Args:
            column: The Iris attribute/column to filter by.
            operator (str): One of '>', '<', '=='
            value: The value to compare the column against.
            order (Optional[str]): 'asc' or 'desc' for ordering.
            limit (Optional[int]): Max number of rows to return.

        Returns:
            List[Iris]: List of Iris entities matching criteria.
        """
        stmt = select(Iris)
        if (species):
            stmt = stmt.join(Species).where(Species.name == species)

        # Apply filter based on operator
        if operator == ">":
            stmt = stmt.filter(column > value)
        elif operator == "<":
            stmt = stmt.filter(column < value)
        elif operator == "==":
            stmt = stmt.filter(column == value)
        else:
            raise ValueError("Operator must be one of '>', '<', '=='")

        # Apply ordering if specified
        if order:
            if order.lower() == "asc":
                stmt = stmt.order_by(asc(column))
            elif order.lower() == "desc":
                stmt = stmt.order_by(desc(column))
            else:
                raise ValueError("Order must be 'asc' or 'desc'")

        # Apply limit if specified
        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    # ----------------- Convenience Methods -----------------

    def get_all_larger_than(self, column, value: float, order: str = "asc", species: str = None) -> List[Iris]:
        """Retrieve all rows where column > value."""
        return self._query_by_column(column, ">", value, order, species=species)

    def get_n_larger_than(self, column, value: float, n: int, order: str = "asc", species: str = None) -> List[Iris]:
        """Retrieve n rows where column > value."""
        return self._query_by_column(column, ">", value, order, limit=n, species=species)

    def get_all_smaller_than(self, column, value: float, order: str = "asc", species: str = None) -> List[Iris]:
        """Retrieve all rows where column < value."""
        return self._query_by_column(column, "<", value, order, species=species)

    def get_n_smaller_than(self, column, value: float, n: int, order: str = "asc", species: str = None) -> List[Iris]:
        """Retrieve n rows where column < value."""
        return self._query_by_column(column, "<", value, order, limit=n, species=species)

    def get_all_equal_to(self, column, value: float, species: str = None) -> List[Iris]:
        """Retrieve all rows where column == value."""
        return self._query_by_column(column, "==", value, species=species)

    def get_n_equal_to(self, column, value: float, n: int, species: str = None) -> List[Iris]:
        """Retrieve n rows where column == value."""
        return self._query_by_column(column, "==", value, limit=n, species=species)

    def get_n(self, n: int, column=None, order: str = "asc", species: str = None) -> List[Iris]:
        """
        Retrieve the first `n` rows, optionally ordered by a column.

        Args:
            n (int): Number of rows to retrieve.
            column: Column to sort by.
            order (str): 'asc' or 'desc' if column is provided.
            species (str): name of species.
        """
        return self._query_by_column(column if column else Iris.id, ">", -float('inf'), order, limit=n, species=species)

    def get_all_by_species(self, name: str) -> List[Iris]:
        """
        Retrieve all rows, optionally ordered by a column.

        Args:
            column: Column to sort by.
            order (str): 'asc' or 'desc' if column is provided.
        """
        return self._query_by_column(Iris.species, "==", name)

    def get_smallest(self, column, species_name: str = None) -> Iris:
        """
        Find row with smallest value in column.
        """
        stmt = select(func.min(column))
        if species_name:
            stmt = stmt.where(Iris.species.has(name=species_name))

        result = self.session.execute(stmt).scalar()
        return float(result) if result is not None else None

    def get_largest(self, column, species_name: str = None) -> Iris:
        """
        Find row with largest value in column.
        """
        stmt = select(func.max(column))
        if species_name:
            stmt = stmt.where(Iris.species.has(name=species_name))

        result = self.session.execute(stmt).scalar()
        return float(result) if result is not None else None

    def get_average(self, column, species_name: str = None) -> float:
        """
        Calculate average of a column, optionally filtered by species.
        """
        stmt = select(func.avg(column))
        if species_name:
            stmt = stmt.where(Iris.species.has(name=species_name))

        result = self.session.execute(stmt).scalar()
        return float(result) if result is not None else None

    def get_median(self, column, species_name: str = None) -> float:
        """
        Calculate median of a column, optionally filtered by species.
        """
        stmt = select(column)
        if species_name:
            stmt = stmt.where(Iris.species.has(name=species_name))

        results = [row[0] for row in self.session.execute(stmt).all()]
        if not results:
            return None
        return float(np.median(results))

    def get_quantile(self, column, q: float, species_name: str = None) -> float:
        """
        Calculate quantile (0 <= q <= 1) of a column, optionally filtered by species.
        """
        if not 0 <= q <= 1:
            raise ValueError("Quantile must be between 0 and 1")

        stmt = select(column)
        if species_name:
            stmt = stmt.where(Iris.species.has(name=species_name))

        results = [row[0] for row in self.session.execute(stmt).all()]
        if not results:
            return None
        return float(np.quantile(results, q))

    def create_iris(self, species_name: str, sepal_length: float, sepal_width: float, petal_length: float, petal_width: float) -> Iris:
        """
        Create a new Iris record.

        - Computes derived fields: sepal_area, petal_area, and ratios.
        - Checks if the species exists by name (case-insensitive).
        - If the species does not exist, creates a new Species record.
        - Commits and refreshes the Iris object.

        Args:
            species_name (str): Name of the species (e.g., "setosa")
            sepal_length (float): Sepal length in cm
            sepal_width (float): Sepal width in cm
            petal_length (float): Petal length in cm
            petal_width (float): Petal width in cm

        Returns:
            Iris: The newly created Iris SQLAlchemy object
        """

        # Compute derived fields
        sepal_area = sepal_length * sepal_width
        petal_area = petal_length * petal_width
        sepal_to_petal_area_ratio = sepal_area / \
            petal_area if petal_area != 0 else None
        sepal_to_petal_length_ratio = sepal_length / \
            petal_length if petal_length != 0 else None
        sepal_to_petal_width_ratio = sepal_width / \
            petal_width if petal_width != 0 else None

        # search for species by name, if doesn't exist create new
        species_name = species_name.lower()
        species = self.session.execute(select(Species).where(
            Species.name == species_name)).scalar_one_or_none()
        if not species:
            species = Species(name=species_name)
            self.session.add(species)
            self.session.commit()
            self.session.refresh(species)

        iris = Iris(
            species_id=species.id,
            sepal_length=sepal_length,
            sepal_width=sepal_width,
            petal_length=petal_length,
            petal_width=petal_width,
            sepal_area=sepal_area,
            petal_area=petal_area,
            sepal_to_petal_area_ratio=sepal_to_petal_area_ratio,
            sepal_to_petal_length_ratio=sepal_to_petal_length_ratio,
            sepal_to_petal_width_ratio=sepal_to_petal_width_ratio
        )
        self.session.add(iris)
        self.session.commit()
        self.session.refresh(iris)
        return iris
