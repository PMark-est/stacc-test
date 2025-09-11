from flask import Flask, jsonify, request, send_from_directory, abort
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from src.repositories import SpeciesRepository, IrisRepository
from src.services import SpeciesService, IrisService
from src.db import get_session, get_engine, seed_if_empty
import sys

app = Flask(__name__)
CORS(app, supports_credentials=True)

# initializes the database
engine = get_engine()
db = get_session(engine)
seed_if_empty(db)

# Initialize repositories and services
species_repo = SpeciesRepository(db)
iris_repo = IrisRepository(db)
app.species_service = SpeciesService(species_repo)
app.iris_service = IrisService(iris_repo)


@app.route("/spec.yaml")
def spec():
    """
    Serve the OpenAPI/Swagger specification file.

    Returns:
        200 OK: YAML spec file.
    """
    return send_from_directory(".", "spec.yaml")


SWAGGER_URL = "/docs"
API_URL = "/spec.yaml"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Iris API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/flowers")
def get_flowers():
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    query_params = request.args.to_dict()
    flowers = app.iris_service.get_flowers(query_params)
    return jsonify(flowers)


@app.route('/flowers', methods=["POST"])
def create_flower():
    """
    Create a new Iris record.

    JSON Body:
        {
            "species_name": str,
            "sepal_length": float,
            "sepal_width": float,
            "petal_length": float,
            "petal_width": float
        }

    Returns:
        201 Created: The created Iris as JSON.
        400 Bad Request: If input data is missing or invalid.
    """
    try:
        species_name = request.json['species_name']
        sepal_length = float(request.json['sepal_length'])
        sepal_width = float(request.json['sepal_width'])
        petal_length = float(request.json['petal_length'])
        petal_width = float(request.json['petal_width'])

        iris = app.iris_service.create_iris(
            species_name, sepal_length, sepal_width, petal_length, petal_width
        )
        return jsonify(iris.to_dict()), 201

    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Invalid input data"}), 400


@app.route("/flowers/<id>")
def get_flower(id):
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    flower = app.iris_service.get_flower_by_id(id)
    return jsonify(flower)


@app.route('/flowers/<id>', methods=['PUT'])
def update_flower(id):
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    data = request.get_json()
    updated_flower = app.iris_service.update_flower(id, data)
    if updated_flower is None:
        abort()
    return jsonify(updated_flower)


@app.route('/flowers/<id>', methods=['DELETE'])
def delete_flower(id):
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    flower = app.iris_service.delete_flower_by_id(id)
    return jsonify(flower)


@app.route("/species")
def get_species():
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    species_list = app.species_service.get_all_species()
    return jsonify(species_list)


@app.route("/species/<species_name>/summary")
def get_summary(species_name: str):
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    flowers = app.iris_service.get_flower_summary(species_name)
    return jsonify(flowers)


@app.route("/statistics")
def get_statistics():
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    stats = app.iris_service.get_stats(app.species_service)
    return jsonify(stats)


@app.route("/statistics/quantile")
def get_quantile():
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    q = float(request.args.get("quantile"))
    species = request.args.get("species")
    feature = request.args.get("measurement")
    stats = app.iris_service.get_quantile(feature, q, species)
    return jsonify(stats)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
