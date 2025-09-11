from src.repositories import SpeciesRepository


class SpeciesService:
    def __init__(self, species_repository: SpeciesRepository):
        self.repo = species_repository

    def get_all_species(self):
        """Get all species."""
        result = self.repo.get_all()
        return [species.to_dict() for species in result]
