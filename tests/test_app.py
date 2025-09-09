import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base
from src.app import app
from src.repositories import SpeciesRepository, IrisRepository
from src.services import SpeciesService, IrisService
from src.db import seed_if_empty


@pytest.fixture
def client():
    # Create in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    test_session = TestingSessionLocal()
    Base.metadata.create_all(bind=engine)

    # Create test repos/services using in-memory session
    test_species_repo = SpeciesRepository(test_session)
    test_iris_repo = IrisRepository(test_session)
    test_species_service = SpeciesService(test_species_repo)
    test_iris_service = IrisService(test_iris_repo)

    # Save original services
    orig_species_service = app.species_service
    orig_iris_service = app.iris_service

    # Override with test services
    app.species_service = test_species_service
    app.iris_service = test_iris_service

    app.config["TESTING"] = True
    try:
        with app.test_client() as client:
            yield client
    finally:
        # Restore original services after test
        app.species_service = orig_species_service
        app.iris_service = orig_iris_service
        test_session.close()


def test_seeding_db(client):
    response = client.get("/species")
    assert response.get_json() == []

    test_session = client.application.species_service.repo.session
    seed_if_empty(test_session)

    response = client.get("/species")
    assert response.get_json() != []
