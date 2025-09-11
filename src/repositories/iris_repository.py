from typing import Dict, List, Optional, Any
from sqlalchemy import select, asc, desc, func
from sqlalchemy.sql import Select
from src.models import Iris, Species
from src.repositories.base_repository import BaseRepository


class IrisRepository(BaseRepository):
    """
    Repository handling Iris persistence and queries.
    """

    def count_by_species(self, species_name: str) -> int:
        """Return count of iris rows for a species."""
        stmt = select(func.count()).select_from(Iris).join(Species).where(
            func.lower(Species.name) == species_name.lower()
        )
        return int(self.session.execute(stmt).scalar() or 0)

    def get_stats(self, column, species_name: Optional[str] = None) -> Optional[Dict[str, float]]:
        """
        Compute basic statistics for a numeric column.
        Returns None when there are no records.
        """
        stmt = select(
            func.avg(column).label("mean"),
            func.min(column).label("min"),
            func.max(column).label("max"),
            func.stddev(column).label("std"),
            func.percentile_cont(0.5).within_group(
                column.asc()).label("median"),
        )
        if species_name:
            stmt = stmt.select_from(Iris).join(Species).where(
                func.lower(Species.name) == species_name.lower())

        result = self.session.execute(stmt).first()
        if not result or result.mean is None:
            return None

        return {
            "mean": float(result.mean),
            "min": float(result.min),
            "max": float(result.max),
            "std": float(result.std) if result.std is not None else 0.0,
            "median": float(result.median) if result.median is not None else None,
        }

    def list_irises(self, params: Dict[str, Any], field_map: Dict[str, Any]) -> List[Iris]:
        """
        Return iris list applying filters, sorting and pagination from params.

        Expected params keys:
            - species (optional)
            - min_<field>, max_<field> (optional range filters)
            - sort_by (optional)
            - sort_order (optional: 'asc'|'desc')
            - limit (optional int)
        """
        stmt = select(Iris).join(Species)

        stmt = self._apply_filters(stmt, params, field_map)
        stmt = self._apply_sorting(stmt, params.get(
            "sort_by"), params.get("sort_order"))

        limit = params.get("limit")
        if limit:
            try:
                stmt = stmt.limit(int(limit))
            except (TypeError, ValueError):
                raise ValueError("limit must be an integer")

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_id(self, iris_id: int) -> Optional[Iris]:
        """Return a single Iris by primary key or None."""
        return self.session.get(Iris, iris_id)

    def update(self, iris_id: int, changes: Dict[str, Any]) -> Optional[Iris]:
        """
        Update an Iris record. Returns the updated entity or None if not found.
        Accepts measurement fields and 'species'.
        """
        iris = self.session.get(Iris, iris_id)
        if iris is None:
            return None

        # Update numeric measurements if present
        measurement_fields = {"sepal_length",
                              "sepal_width", "petal_length", "petal_width"}
        for key, val in changes.items():
            if key in measurement_fields:
                setattr(iris, key, float(val))
        # Update species if provided: find or create
        if "species" in changes:
            species_name = str(changes["species"]).lower()
            species = self.session.execute(select(Species).where(
                func.lower(Species.name) == species_name)).scalar_one_or_none()
            if not species:
                species = Species(name=species_name)
                self.session.add(species)
                self.session.flush()
            iris.species = species
            iris.species_id = species.id

        # Recompute dependent features (areas/ratios)
        self._recompute_derived(iris)

        self.session.commit()
        self.session.refresh(iris)
        return iris

    def delete_by_id(self, iris_id: int) -> bool:
        """Delete iris by id. Returns True if deleted, False if not found."""
        iris = self.session.get(Iris, iris_id)
        if iris is None:
            return False
        self.session.delete(iris)
        self.session.commit()
        return True

    def create(self, species_name: str, sepal_length: float, sepal_width: float, petal_length: float, petal_width: float) -> Iris:
        """Create and persist an Iris row; returns the created Iris."""
        # Ensure species exists (case-insensitive)
        species_name_lower = species_name.lower()
        species = self.session.execute(select(Species).where(
            func.lower(Species.name) == species_name_lower)).scalar_one_or_none()
        if not species:
            species = Species(name=species_name_lower)
            self.session.add(species)
            self.session.flush()
            self.session.refresh(species)

        iris = Iris(
            species_id=species.id,
            sepal_length=float(sepal_length),
            sepal_width=float(sepal_width),
            petal_length=float(petal_length),
            petal_width=float(petal_width),
        )
        # compute derived fields
        self._recompute_derived(iris)

        iris.species = species
        self.session.add(iris)
        self.session.commit()
        self.session.refresh(iris)
        return iris

    def get_quantile(self, column, quantile: float, species_name: Optional[str] = None) -> Optional[float]:
        """
        Compute the q-th quantile (0 <= q <= 1) of a numeric column.
        Returns None if no records.
        """
        stmt = select(
            func.percentile_cont(quantile).within_group(
                column.asc()).label("q")
        )
        if species_name:
            stmt = stmt.select_from(Iris).join(Species).where(
                func.lower(Species.name) == species_name.lower())
        result = self.session.execute(stmt).scalar()
        return float(result) if result is not None else None

    # --- Internal helpers -------------------------------------------------

    def _recompute_derived(self, iris: Iris) -> None:
        """Compute derived features (areas and ratios) on an Iris instance."""
        iris.sepal_area = iris.sepal_length * iris.sepal_width
        iris.petal_area = iris.petal_length * iris.petal_width
        iris.sepal_to_petal_area_ratio = iris.sepal_area / \
            iris.petal_area if iris.petal_area != 0 else None
        iris.sepal_to_petal_length_ratio = iris.sepal_length / \
            iris.petal_length if iris.petal_length != 0 else None
        iris.sepal_to_petal_width_ratio = iris.sepal_width / \
            iris.petal_width if iris.petal_width != 0 else None

    def _apply_filters(self, stmt: Select, params: Dict[str, Any], field_map: Dict[str, Any]) -> Select:
        """Apply species and numeric range filters to a statement."""
        # species filter (case-insensitive)
        species = params.get("species")
        if species:
            stmt = stmt.where(func.lower(Species.name) == str(species).lower())

        # numeric range filters of form min_<field>, max_<field>
        for field_key in field_map.keys():
            min_k = f"min_{field_key}"
            max_k = f"max_{field_key}"
            field_attr = field_map[field_key]

            if min_k in params:
                try:
                    min_val = float(params[min_k])
                    stmt = stmt.where(field_attr >= min_val)
                except (ValueError, TypeError):
                    raise ValueError(f"{min_k} must be a number")
            if max_k in params:
                try:
                    max_val = float(params[max_k])
                    stmt = stmt.where(field_attr <= max_val)
                except (ValueError, TypeError):
                    raise ValueError(f"{max_k} must be a number")

        return stmt

    def _apply_sorting(self, stmt: Select, sort_by: Optional[str], sort_order: Optional[str]) -> Select:
        """Apply ordering; 'species' sorts by Species.name; other keys map to Iris attributes."""
        if not sort_by:
            return stmt

        if sort_by == "species":
            stmt = stmt.join(Species)
            sort_col = Species.name
        else:
            sort_col = getattr(Iris, sort_by)

        if (sort_order or "").lower() == "asc":
            stmt = stmt.order_by(asc(sort_col))
        else:
            stmt = stmt.order_by(desc(sort_col))
        return stmt
