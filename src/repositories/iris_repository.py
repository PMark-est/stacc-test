from sqlalchemy import select, asc, desc, func
from typing import Dict, List, Optional
from src.models import Species, Iris
from src.repositories.base_repository import BaseRepository


class IrisRepository(BaseRepository):
    """
    Repository class for handling database operations on Iris entities.

    Provides query helpers for filtering, aggregating, and creating `Iris` records.
    """

    def get_all_by_species(self, species_name: str) -> List[Iris]:
        """
        Retrieve all rows for a given species.

        Args:
            species_name (str): Name of the species.

        Returns:
            List[Iris]: List of Iris objects belonging to the species.
        """
        stmt = select(Iris).join(Species).where(Species.name == species_name)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_flowers_amount(self, species_name):
        stmt = select(func.count()).select_from(Iris).join(
            Species).where(Species.name == species_name)
        result = self.session.execute(stmt)
        return result.scalar()

    def get_stats(self, column, species_name: str = None):
        stmt = select(
            func.avg(column).label('mean'),
            func.min(column).label('min'),
            func.max(column).label('max'),
            func.stddev(column).label('std'),
            func.percentile_cont(0.5).within_group(
                column.asc()).label('median')
        )

        # Add species filter if provided
        if species_name:
            stmt = stmt.join(Species).where(Species.name == species_name)

        result = self.session.execute(stmt).first()

        if not result or result.mean is None:
            return None

        return {
            "mean": float(result.mean),
            "min": float(result.min),
            "max": float(result.max),
            "std": float(result.std) if result.std is not None else 0.0,
            "median": float(result.median) if result.median is not None else None
        }

    def get_flowers(self, params, fields, sort_by, sort_order) -> List[Iris]:
        stmt = select(Iris).join(Species)

        stmt = self._apply_filters(stmt, params, fields)
        stmt = self._apply_sorting(stmt, sort_by, sort_order)

        if params["limit"]:
            stmt = stmt.limit(params["limit"])

        result = self.session.execute(stmt)
        flowers = list(result.scalars().all())
        return flowers

    def get_flower_by_id(self, id: int) -> Iris:
        stmt = select(Iris).where(Iris.id == id)
        result = self.session.execute(stmt)

        return result.scalar()

    # In your IrisRepository class

    def update_flower(self, flower_id: int, update_data: Dict[str, any]) -> Optional[Iris]:
        """
        Update an existing iris flower record.

        Args:
            flower_id (int): ID of the flower to update
            update_data (Dict): Dictionary of fields to update

        Returns:
            Optional[Iris]: Updated Iris object, or None if not found
        """
        # First get the existing flower
        flower = self.session.get(Iris, flower_id)
        if flower is None:
            return None

        # Update basic fields
        if 'sepal_length' in update_data:
            flower.sepal_length = update_data['sepal_length']
        if 'sepal_width' in update_data:
            flower.sepal_width = update_data['sepal_width']
        if 'petal_length' in update_data:
            flower.petal_length = update_data['petal_length']
        if 'petal_width' in update_data:
            flower.petal_width = update_data['petal_width']

        # Update species if provided
        if 'species' in update_data:
            species_name = update_data['species'].lower()
            # Find or create species
            species = self.session.execute(
                select(Species).where(Species.name == species_name)
            ).scalar_one_or_none()

            if not species:
                species = Species(name=species_name)
                self.session.add(species)
                self.session.flush()  # Flush to get the ID

            flower.species_id = species.id
            flower.species = species  # Assign the species object directly

        # Recalculate derived fields if any measurements changed
        measurement_fields = ['sepal_length',
                              'sepal_width', 'petal_length', 'petal_width']
        if any(field in update_data for field in measurement_fields):
            flower.sepal_area = flower.sepal_length * flower.sepal_width

            flower.petal_area = flower.petal_length * flower.petal_width

            flower.sepal_to_petal_area_ratio = flower.sepal_area / \
                flower.petal_area if flower.petal_area != 0 else None
            flower.sepal_to_petal_length_ratio = flower.sepal_length / \
                flower.petal_length if flower.petal_length != 0 else None
            flower.sepal_to_petal_width_ratio = flower.sepal_width / \
                flower.petal_width if flower.petal_width != 0 else None

        self.session.commit()
        self.session.refresh(flower)
        return flower

    def delete_flower_by_id(self, flower_id: int) -> bool:
        """
        Delete an iris flower record by ID.

        Args:
            flower_id (int): ID of the flower to delete

        Returns:
            bool: True if deleted, False if not found
        """
        flower = self.session.get(Iris, flower_id)
        if flower is None:
            return None

        self.session.delete(flower)
        self.session.commit()
        return True

    def _apply_filters(self, stmt, params: Dict[str, str], fields: List[str]):
        """Apply all filters to the SQLAlchemy statement"""

        # Species filter
        if 'species' in params:
            species_name = params['species'].lower()
            stmt = stmt.where(Species.name == species_name)

        # Apply range filters
        for field in fields:
            min_key = f'min_{field}'
            max_key = f'max_{field}'

            if min_key in params:
                try:
                    min_val = float(params[min_key])
                    stmt = stmt.where(fields[field] >= min_val)
                except ValueError:
                    raise ValueError(
                        f"Invalid value for {min_key}. Must be a number")

            if max_key in params:
                try:
                    max_val = float(params[max_key])
                    stmt = stmt.where(fields[field] <= max_val)
                except ValueError:
                    raise ValueError(
                        f"Invalid value for {max_key}. Must be a number")

        return stmt

    def _apply_sorting(self, stmt, sort_by: str, sort_order: str):
        """Apply sorting to the SQLAlchemy statement"""

        # Handle species sorting (requires join)
        if not sort_by:
            pass
        elif sort_by == 'species':
            stmt = stmt.join(Species)
            sort_column = Species.name
        else:
            sort_column = getattr(Iris, sort_by)

        # Apply ordering
        if not sort_order:
            pass
        elif sort_order == 'asc':
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        return stmt

    def create_iris(self, species_name: str, sepal_length: float, sepal_width: float, petal_length: float, petal_width: float) -> Iris:
        """
        Create and persist a new Iris record.

        - Computes derived fields: sepal_area, petal_area, and ratios.
        - Ensures the species exists (creates it if missing).
        - Commits and refreshes the new record.

        Args:
            species_name (str): Name of the species (case-insensitive).
            sepal_length (float): Sepal length in cm.
            sepal_width (float): Sepal width in cm.
            petal_length (float): Petal length in cm.
            petal_width (float): Petal width in cm.

        Returns:
            Iris: The newly created Iris object.
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

        # Ensure species exists
        species_name = species_name.lower()
        species = self.session.execute(
            select(Species).where(Species.name == species_name)
        ).scalar_one_or_none()
        if not species:
            species = Species(name=species_name)
            self.session.add(species)
            self.session.commit()
            self.session.refresh(species)

        # Create Iris record
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
