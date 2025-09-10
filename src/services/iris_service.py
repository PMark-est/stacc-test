from typing import List, Optional, Dict, Any
from src.repositories import IrisRepository
from src.models import Iris


class IrisService:
    """
    A service class that provides business logic and operations for Iris entities.

    This class acts as an intermediary between the API layer and the repository layer,
    handling data validation, transformation, and business rules for Iris data.

    Attributes:
        repo (IrisRepository): The repository instance for database operations.
        column_map (Dict[str, Any]): Mapping of column names to SQLAlchemy attributes.
    """

    def __init__(self, iris_repository: IrisRepository) -> None:
        """
        Initialize the IrisService with a repository instance.

        Args:
            iris_repository (IrisRepository): The repository instance for database operations.
        """
        self.repo = iris_repository
        self.column_map = {
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
        return list(self.column_map.keys())

    def validate_column(self, column: str) -> bool:
        """
        Validate if a column exists in the available column map.

        Args:
            column (str): The column name to validate.

        Returns:
            bool: True if the column exists, False otherwise.
        """
        return column in self.column_map

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
        if column not in self.column_map:
            raise ValueError(
                f"Column '{column}' is not available for querying.")
        return self.column_map[column]

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

    def get_larger_than(
        self,
        column: str,
        value: float,
        n: Optional[int] = None,
        order: str = "asc",
        species_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get iris records where the column value is larger than the specified value.

        Args:
            column (str): The column name to filter by.
            value (float): The threshold value.
            n (Optional[int]): Number of records to return (None for all).
            order (str): Sort order ('asc' or 'desc'). Defaults to 'asc'.
            species (Optional[str]): Optional species filter.

        Returns:
            List[Dict[str, Any]]: List of iris records as dictionaries.
        """
        col = self.get_column_attribute(column)

        if n:
            result = self.repo.get_n_larger_than(
                col, value, n, order, species_name=species_name)
        else:
            result = self.repo.get_all_larger_than(
                col, value, order, species_name=species_name)

        return [iris.to_dict() for iris in result]

    def get_smaller_than(
        self,
        column: str,
        value: float,
        n: Optional[int] = None,
        order: str = "asc",
        species_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get iris records where the column value is smaller than the specified value.

        Args:
            column (str): The column name to filter by.
            value (float): The threshold value.
            n (Optional[int]): Number of records to return (None for all).
            order (str): Sort order ('asc' or 'desc'). Defaults to 'asc'.
            species (Optional[str]): Optional species filter.

        Returns:
            List[Dict[str, Any]]: List of iris records as dictionaries.
        """
        col = self.get_column_attribute(column)

        if n:
            result = self.repo.get_n_smaller_than(
                col, value, n, order, species_name=species_name)
        else:
            result = self.repo.get_all_smaller_than(
                col, value, order, species_name=species_name)

        return [iris.to_dict() for iris in result]

    def get_equal_to(
        self,
        column: str,
        value: float,
        n: Optional[int] = None,
        species_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get iris records where the column value equals the specified value.

        Args:
            column (str): The column name to filter by.
            value (float): The value to match.
            n (Optional[int]): Number of records to return (None for all).
            species (Optional[str]): Optional species filter.

        Returns:
            List[Dict[str, Any]]: List of iris records as dictionaries.
        """
        col = self.get_column_attribute(column)

        if n:
            result = self.repo.get_n_equal_to(
                col, value, n, species_name=species_name)
        else:
            result = self.repo.get_all_equal_to(
                col, value, species_name=species_name)

        return [iris.to_dict() for iris in result]

    def get_n(
        self,
        column: str,
        n: int,
        order: str = "asc",
        species_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get the top N iris records ordered by the specified column.

        Args:
            column (str): The column name to order by.
            n (int): Number of records to return.
            order (str): Sort order ('asc' or 'desc'). Defaults to 'asc'.
            species (Optional[str]): Optional species filter.

        Returns:
            List[Dict[str, Any]]: List of iris records as dictionaries.
        """
        col = self.get_column_attribute(column)
        result = self.repo.get_n(
            n, column=col, order=order, species_name=species_name)
        return [iris.to_dict() for iris in result]

    def get_smallest_value(
        self, column: str, species: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the smallest value for a column, optionally filtered by species.

        Args:
            column (str): The column name to analyze.
            species (Optional[str]): Optional species filter.

        Returns:
            Dict[str, Any]: Dictionary containing column, species, and value information.
        """
        col = self.get_column_attribute(column)
        smallest = self.repo.get_smallest(col, species_name=species)
        return {"column": column, "species": species, "value": smallest}

    def get_largest_value(
        self, column: str, species: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the largest value for a column, optionally filtered by species.

        Args:
            column (str): The column name to analyze.
            species (Optional[str]): Optional species filter.

        Returns:
            Dict[str, Any]: Dictionary containing column, species, and value information.
        """
        col = self.get_column_attribute(column)
        largest = self.repo.get_largest(col, species_name=species)
        return {"column": column, "species": species, "value": largest}

    def get_average_value(
        self, column: str, species: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the average value for a column, optionally filtered by species.

        Args:
            column (str): The column name to analyze.
            species (Optional[str]): Optional species filter.

        Returns:
            Dict[str, Any]: Dictionary containing column, species, and value information.
        """
        col = self.get_column_attribute(column)
        avg_value = self.repo.get_average(col, species_name=species)
        return {"column": column, "species": species, "value": avg_value}

    def get_median_value(
        self, column: str, species: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the median value for a column, optionally filtered by species.

        Args:
            column (str): The column name to analyze.
            species (Optional[str]): Optional species filter.

        Returns:
            Dict[str, Any]: Dictionary containing column, species, and value information.
        """
        col = self.get_column_attribute(column)
        median_value = self.repo.get_median(col, species_name=species)
        return {"column": column, "species": species, "value": median_value}

    def get_quantile_value(
        self, column: str, q: float, species: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the quantile value for a column, optionally filtered by species.

        Args:
            column (str): The column name to analyze.
            q (float): The quantile to calculate (0.0 to 1.0).
            species (Optional[str]): Optional species filter.

        Returns:
            Dict[str, Any]: Dictionary containing column, species, quantile, and value information.
        """
        col = self.get_column_attribute(column)
        quantile_value = self.repo.get_quantile(col, q, species_name=species)
        return {"column": column, "species": species, "quantile": q, "value": quantile_value}
