from typing import List, Dict
from src.repositories import SpeciesRepository


class SpeciesService:
    """Service wrapper around SpeciesRepository."""

    def __init__(self, species_repository: SpeciesRepository) -> None:
        self.repo = species_repository

    def get_all_species(self) -> List[Dict[str, str]]:
        """Return list of species as dicts."""
        rows = self.repo.get_all()
        return [r.to_dict() for r in rows]
