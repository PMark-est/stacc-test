from typing import List, Optional, Dict, Any
from src.repositories import IrisRepository
from src.models import Iris, Species
from src.services.species_service import SpeciesService
import sys


class IrisService:
    """
    A service class that provides business logic and operations for Iris entities.

    This class acts as an intermediary between the API layer and the repository layer,
    handling data validation, transformation, and business rules for Iris data.

    Attributes:
        repo (IrisRepository): The repository instance for database operations.
        field_map (Dict[str, Any]): Mapping of column names to SQLAlchemy attributes.
    """

    def __init__(self, iris_repository: IrisRepository) -> None:
        """
        Initialize the IrisService with a repository instance.

        Args:
            iris_repository (IrisRepository): The repository instance for database operations.
        """
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

    def create_iris(
        self,
        species_name: str,
        sepal_length: float,
        sepal_width: float,
        petal_length: float,
        petal_width: float,
    ) -> Dict[str, Any]:
        """
        Create a new iris record in the database.

        Args:
            species_name (str): The name of the species.
            sepal_length (float): The sepal length measurement.
            sepal_width (float): The sepal width measurement.
            petal_length (float): The petal length measurement.
            petal_width (float): The petal width measurement.

        Returns:
            Dict[str, Any]: The created iris record as a dictionary.
        """
        iris = self.repo.create_iris(
            species_name, sepal_length, sepal_width, petal_length, petal_width)
        return iris.to_dict()

    def get_available_columns(self) -> List[str]:
        """
        Get a list of all available columns for querying.

        Returns:
            List[str]: List of column names that can be used in queries.
        """
        return list(self.field_map.keys())

    def validate_column(self, column: str) -> bool:
        """
        Validate if a column exists in the available column map.

        Args:
            column (str): The column name to validate.

        Returns:
            bool: True if the column exists, False otherwise.
        """
        return column in self.field_map

    def get_column_attribute(self, column: str) -> Any:
        """
        Get the SQLAlchemy column attribute for a given column name.

        Args:
            column (str): The column name to look up.

        Returns:
            Any: The SQLAlchemy column attribute, or None if not found.

        Raises:
            ValueError: If the column is not found in the column map.
        """
        if column not in self.field_map:
            raise ValueError(
                f"Column '{column}' is not available for querying.")
        return self.field_map[column]

    def get_all_by_species(self, species_name: str) -> List[Dict[str, Any]]:
        """
        Get all iris records for a specific species.

        Args:
            species_name (str): The name of the species to filter by.

        Returns:
            List[Dict[str, Any]]: List of iris records as dictionaries.
        """
        result = self.repo.get_all_by_species(species_name)
        return [iris.to_dict() for iris in result]

    # List[Iris.to_dict]
    def get_flowers(self, params) -> List[Dict[str, str]]:
        sort_by = params["sort_by"]
        if sort_by and sort_by not in self.field_map:
            raise ValueError(
                f"Invalid sort field. Must be one of: {', '.join(self.field_map.keys())}")

        sort_order = params["sort_order"]
        if sort_order and sort_order not in ['asc', 'desc']:
            raise ValueError("Invalid sort order. Must be 'asc' or 'desc'")

        flowers = self.repo.get_flowers(
            params, self.field_map, sort_by, sort_order)
        return [flower.to_dict() for flower in flowers]

    def get_flower_by_id(self, id) -> Dict[str, str]:  # Iris.to_dict
        return self.repo.get_flower_by_id(id).to_dict()

    def update_flower(self, flower_id: int, update_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Update a flower and return the result.

        Args:
            flower_id (int): ID of the flower to update
            update_data (Dict): Fields to update

        Returns:
            Dict: Result with status and data/error
        """
        # Validate input
        if not update_data:
            return "No data provided"

        valid_features = ['sepal_length', 'species',
                          'sepal_width', 'petal_length', 'petal_width']

        for field in update_data:
            if field not in valid_features:
                raise ValueError(f"Field {field} is not a valid feature")

        for field in update_data:
            if field == "species":
                continue
            try:
                value = float(update_data[field])
                if value <= 0:
                    return {"status": "error", "message": f"{field} must be positive"}
            except (ValueError, TypeError):
                return {"status": "error", "message": f"{field} must be a number"}

        # Update the flower
        updated_flower = self.repo.update_flower(flower_id, update_data)

        if not updated_flower:
            raise ValueError(f"Flower with ID {flower_id} not found")

        if updated_flower is None:
            return None
        return updated_flower.to_dict()

    def delete_flower_by_id(self, flower_id: int) -> Dict[str, Any]:
        """
        Delete a flower by ID.

        Args:
            flower_id (int): ID of the flower to delete

        Returns:
            Dict: Result with status and message
        """
        success = self.repo.delete_flower_by_id(flower_id)

        if success is None:
            return None

        return {"status": "success", "message": f"Flower with ID {flower_id} deleted successfully"}

    def get_stats(self, species_service: SpeciesService):
        species_list = species_service.get_all_species()
        cols = self.get_available_columns()
        stats = {"species_distribution": {}, "measurements": {}}
        for species in species_list:
            species_name = species["name"]
            stats["species_distribution"][species_name] = self.repo.get_flowers_amount(
                species_name)
            for col in cols:
                column = self.field_map[col]
                stats["measurements"][col] = self.repo.get_stats(column)
        stats["total_records"] = sum(stats["species_distribution"].values())
        return stats

    def get_flower_summary(self, species_name: str):
        cols = self.get_available_columns()
        stats = {"measurements": {}}
        stats["total_records"] = self.repo.get_flowers_amount(species_name)
        for col in cols:
            column = self.field_map[col]
            stats["measurements"][col] = self.repo.get_stats(
                column, species_name)
        return stats
