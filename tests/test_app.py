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
    """
    Provide a Flask test client backed by an in-memory SQLite DB.
    We swap the app services to use the test DB session and restore afterwards.
    """
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    test_session = TestingSessionLocal()
    Base.metadata.create_all(bind=engine)

    # Create test repos/services using in-memory session
    test_species_repo = SpeciesRepository(test_session)
    test_iris_repo = IrisRepository(test_session)
    test_species_service = SpeciesService(test_species_repo)
    test_iris_service = IrisService(test_iris_repo)

    # Save original services to restore later
    orig_species_service = app.species_service
    orig_iris_service = app.iris_service

    # Replace services with test instances
    app.species_service = test_species_service
    app.iris_service = test_iris_service

    app.config["TESTING"] = True
    try:
        with app.test_client() as client:
            yield client
    finally:
        # restore
        app.species_service = orig_species_service
        app.iris_service = orig_iris_service
        test_session.close()


def test_seed_and_list_species(client):
    # Initially no species
    resp = client.get("/species")
    assert resp.status_code == 200
    assert resp.get_json() == []

    # seed db via repository session used in app
    test_session = client.application.species_service.repo.session
    seed_if_empty(test_session)  # should populate DB

    resp = client.get("/species")
    assert resp.status_code == 200
    assert resp.get_json() != []


def test_crud_iris(client):
    # Create iris
    payload = {
        "species_name": "setosa",
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    resp = client.post("/irises", json=payload)
    assert resp.status_code == 201
    iris = resp.get_json()
    assert iris["species"] == "setosa"

    iris_id = iris["id"]

    # Get it
    resp = client.get(f"/irises/{iris_id}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == iris_id

    # Update it
    resp = client.put(f"/irises/{iris_id}", json={"sepal_length": 6.0})
    assert resp.status_code == 200
    assert resp.get_json()["sepal_length"] == 6.0

    # Delete it
    resp = client.delete(f"/irises/{iris_id}")
    assert resp.status_code == 200

    # Not found afterwards
    resp = client.get(f"/irises/{iris_id}")
    assert resp.status_code == 404
