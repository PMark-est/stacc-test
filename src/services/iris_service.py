from typing import List, Optional, Dict, Any
from repositories import IrisRepository
from src.models import Iris


class IrisService:
    def __init__(self, iris_repository: IrisRepository):
        self.iris_repo = iris_repository
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

    def create_iris(self, species_name: str, sepal_length: float, sepal_width: float, petal_length: float, petal_width: float):
        """Create a new iris record."""
        return self.iris_repo.create_iris(species_name, sepal_length, sepal_width, petal_length, petal_width)

    def get_available_columns(self) -> List[str]:
        """Get list of available columns for querying."""
        return list(self.column_map.keys())

    def validate_column(self, column: str) -> bool:
        """Validate if column exists in the column map."""
        return column in self.column_map

    def get_column_attribute(self, column: str):
        """Get the SQLAlchemy column attribute for a given column name."""
        return self.column_map.get(column)

    def get_all_by_species(self, species_name: str) -> List[Dict[str, Any]]:
        """Get all iris records for a specific species."""
        result = self.iris_repo.get_all_by_species(species_name)
        return [iris.to_dict() for iris in result]

    def get_larger_than(self, column: str, value: float, n: Optional[int] = None,
                        order: str = "asc") -> List[Dict[str, Any]]:
        """Get iris records where column value is larger than specified value."""
        col = self.get_column_attribute(column)

        if n:
            result = self.iris_repo.get_n_larger_than(col, value, n, order)
        else:
            result = self.iris_repo.get_all_larger_than(col, value, order)

        return [iris.to_dict() for iris in result]

    def get_smaller_than(self, column: str, value: float, n: Optional[int] = None,
                         order: str = "asc") -> List[Dict[str, Any]]:
        """Get iris records where column value is smaller than specified value."""
        col = self.get_column_attribute(column)

        if n:
            result = self.iris_repo.get_n_smaller_than(col, value, n, order)
        else:
            result = self.iris_repo.get_all_smaller_than(col, value, order)

        return [iris.to_dict() for iris in result]

    def get_equal_to(self, column: str, value: float, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get iris records where column value equals specified value."""
        col = self.get_column_attribute(column)

        if n:
            result = self.iris_repo.get_n_equal_to(col, value, n)
        else:
            result = self.iris_repo.get_all_equal_to(col, value)

        return [iris.to_dict() for iris in result]

    def get_top_n(self, column: str, n: int, order: str = "asc") -> List[Dict[str, Any]]:
        """Get top N iris records ordered by specified column."""
        col = self.get_column_attribute(column)
        result = self.iris_repo.get_n(n, column=col, order=order)
        return [iris.to_dict() for iris in result]

    def get_smallest_value(self, column: str, species: Optional[str] = None) -> Dict[str, Any]:
        """Get the smallest value for a column, optionally filtered by species."""
        col = self.get_column_attribute(column)
        smallest = self.iris_repo.get_smallest(col, species_name=species)
        return {"column": column, "species": species, "value": smallest}

    def get_largest_value(self, column: str, species: Optional[str] = None) -> Dict[str, Any]:
        """Get the largest value for a column, optionally filtered by species."""
        col = self.get_column_attribute(column)
        largest = self.iris_repo.get_largest(col, species_name=species)
        return {"column": column, "species": species, "value": largest}

    def get_average_value(self, column: str, species: Optional[str] = None) -> Dict[str, Any]:
        """Get the average value for a column, optionally filtered by species."""
        col = self.get_column_attribute(column)
        avg_value = self.iris_repo.get_average(col, species_name=species)
        return {"column": column, "species": species, "value": avg_value}

    def get_median_value(self, column: str, species: Optional[str] = None) -> Dict[str, Any]:
        """Get the median value for a column, optionally filtered by species."""
        col = self.get_column_attribute(column)
        median_value = self.iris_repo.get_median(col, species_name=species)
        return {"column": column, "species": species, "value": median_value}

    def get_quantile_value(self, column: str, q: float, species: Optional[str] = None) -> Dict[str, Any]:
        """Get the quantile value for a column, optionally filtered by species."""
        col = self.get_column_attribute(column)
        quantile_value = self.iris_repo.get_quantile(
            col, q, species_name=species)
        return {"column": column, "species": species, "quantile": q, "value": quantile_value}
