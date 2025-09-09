from repositories import SpeciesRepository


class SpeciesService:
    def __init__(self, species_repository: SpeciesRepository):
        self.species_repo = species_repository

    def get_all_species(self):
        """Get all species as a list of dictionaries."""
        result = self.species_repo.get_all()
        return [species.to_dict() for species in result]
