from typing import List, Dict, Any, Optional
from src.repositories import IrisRepository
from src.models import Iris
from src.services.species_service import SpeciesService


class IrisService:
    """
    Business logic layer for Iris domain.
    """

    def __init__(self, iris_repository: IrisRepository) -> None:
        self.repo = iris_repository
        self.field_map = {
            "sepal_length": Iris.sepal_length,
            "sepal_width": Iris.sepal_width,
            "petal_length": Iris.petal_length,
            "petal_width": Iris.petal_width,
            "sepal_area": Iris.sepal_area,
            "petal_area": Iris.petal_area,
            "sepal_to_petal_area_ratio": Iris.sepal_to_petal_area_ratio,
            "sepal_to_petal_length_ratio": Iris.sepal_to_petal_length_ratio,
            "sepal_to_petal_width_ratio": Iris.sepal_to_petal_width_ratio,
        }

    # --- Create / Read / Update / Delete --------------------------------

    def create_iris(self, species_name: str, sepal_length: float, sepal_width: float, petal_length: float, petal_width: float) -> Dict[str, Any]:
        created = self.repo.create(
            species_name, sepal_length, sepal_width, petal_length, petal_width)
        return created.to_dict()

    def list_irises(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return list of iris dicts after validating sorting params."""
        sort_by = params.get("sort_by")
        if sort_by and sort_by not in self.field_map and sort_by != "species":
            raise ValueError(
                f"Invalid sort field. Must be one of: {', '.join(list(self.field_map.keys()) + ['species'])}")

        sort_order = params.get("sort_order")
        if sort_order and sort_order.lower() not in {"asc", "desc"}:
            raise ValueError("Invalid sort order. Must be 'asc' or 'desc'")

        rows = self.repo.list_irises(params, self.field_map)
        return [r.to_dict() for r in rows]

    def get_iris_by_id(self, iris_id: int) -> Optional[Dict[str, Any]]:
        row = self.repo.get_by_id(int(iris_id))
        if not row:
            return None
        return row.to_dict()

    def update_iris(self, iris_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate update data and perform update; returns updated dict or None."""
        if not update_data:
            raise ValueError("No data provided for update")

        valid_keys = {"sepal_length", "sepal_width",
                      "petal_length", "petal_width", "species_name"}
        for k in update_data.keys():
            if k not in valid_keys:
                raise ValueError(f"Invalid field in update payload: {k}")

        # Validate numeric fields
        for k in ("sepal_length", "sepal_width", "petal_length", "petal_width"):
            if k in update_data:
                try:
                    val = float(update_data[k])
                except (TypeError, ValueError):
                    raise ValueError(f"{k} must be a number")
                if val <= 0:
                    raise ValueError(f"{k} must be positive")

        updated = self.repo.update(int(iris_id), update_data)
        if updated is None:
            return None
        return updated.to_dict()

    def delete_iris_by_id(self, iris_id: int) -> bool:
        """Delete an iris; return True if deleted, False if not found."""
        return self.repo.delete_by_id(int(iris_id))

    # --- Aggregation / Statistics ---------------------------------------

    def get_available_columns(self) -> List[str]:
        return list(self.field_map.keys())

    def get_summary_for_species(self, species_name: str) -> Dict[str, Any]:
        """Return per-measurement statistics and total records for a single species."""
        cols = self.get_available_columns()
        summary = {"measurements": {}}
        summary["total_records"] = self.repo.count_by_species(species_name)
        for col in cols:
            attr = self.field_map[col]
            summary["measurements"][col] = self.repo.get_stats(
                attr, species_name)
        return summary

    def get_stats_for_species(self, species_service: SpeciesService) -> Dict[str, Any]:
        """
        Build statistics summary across species and measurements.
        Note: measurement stats are computed across all species (and per-species when requested).
        """
        species_list = species_service.get_all_species()
        cols = self.get_available_columns()
        stats = {"species_distribution": {}, "measurements": {}}
        for species in species_list:
            name = species["name"]
            stats["species_distribution"][name] = self.repo.count_by_species(
                name)

        # measurement stats across entire dataset
        for col in cols:
            attr = self.field_map[col]
            stats["measurements"][col] = self.repo.get_stats(attr)

        stats["total_records"] = sum(stats["species_distribution"].values())
        return stats

    def get_quantile(self, column_name: str, quantile: float, species_name: Optional[str] = None) -> Optional[float]:
        """
        Compute quantile for a measurement column.
        Raises ValueError for invalid inputs.
        """
        if column_name not in self.field_map:
            raise ValueError(
                f"Invalid column '{column_name}'. Must be one of: {', '.join(self.field_map.keys())}")
        if not (0 <= quantile <= 1):
            raise ValueError("Quantile must be between 0 and 1")

        column = self.field_map[column_name]
        return self.repo.get_quantile(column, quantile, species_name)
