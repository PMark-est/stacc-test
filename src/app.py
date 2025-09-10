from flask import Flask, jsonify, request, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from src.repositories import SpeciesRepository, IrisRepository
from src.services import SpeciesService, IrisService
from src.db import get_session, get_engine, seed_if_empty

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


# Swagger UI setup
SWAGGER_URL = "/docs"  # URL for exposing Swagger UI
API_URL = "/spec.yaml"  # Our spec file
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Iris API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/iris', methods=["POST"])
def add_iris():
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


@app.route("/species/count")
def get_species_count():
    """
    Retrieve amount of different species.

    Returns:
        200 OK: Amount of different species.
    """
    count = app.species_service.get_count()
    return jsonify(count)


@app.route("/species")
def get_species():
    """
    Retrieve all available species.

    Returns:
        200 OK: List of species as JSON.
    """
    species_list = app.species_service.get_all_species()
    return jsonify(species_list)


@app.route("/iris/columns")
def get_columns():
    """
    Retrieve all available numeric columns for Iris queries.

    Returns:
        200 OK: List of column names as JSON.
    """
    columns = app.iris_service.get_available_columns()
    return jsonify(columns)


@app.route("/iris/<name>")
def get_all_by_species(name):
    """
    Retrieve all Iris records for a given species.

    Path Params:
        name (str): Species name.

    Returns:
        200 OK: List of Iris records as JSON.
    """
    iris_list = app.iris_service.get_all_by_species(name)
    return jsonify(iris_list)


@app.route("/iris/<column>/larger_than")
def get_larger_than(column):
    """
    Retrieve Iris rows where a column is greater than a value.

    Path Params:
        column (str): Column name.

    Query Params:
        value (float): Threshold value (required).
        n (int): Max number of rows (optional).
        order (str): "asc" or "desc" (default: "asc").
        species (str): Filter by species (optional).

    Returns:
        200 OK: List of Iris records as JSON.
        400 Bad Request: If parameters are invalid.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    try:
        species = request.args.get("species")
        value = float(request.args.get("value"))
        n = request.args.get("n", type=int)
        order = request.args.get("order", "asc")
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid value parameter"}), 400

    iris_list = app.iris_service.get_larger_than(
        column, value, n, order, species
    )
    return jsonify(iris_list)


@app.route("/iris/<column>/smaller_than")
def get_smaller_than(column):
    """
    Retrieve Iris rows where a column is smaller than a value.

    Path Params:
        column (str): Column name.

    Query Params:
        value (float): Threshold value (required).
        n (int): Max number of rows (optional).
        order (str): "asc" or "desc" (default: "asc").
        species (str): Filter by species (optional).

    Returns:
        200 OK: List of Iris records as JSON.
        400 Bad Request: If parameters are invalid.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    try:
        species = request.args.get("species")
        value = float(request.args.get("value"))
        n = request.args.get("n", type=int)
        order = request.args.get("order", "asc")
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid value parameter"}), 400

    iris_list = app.iris_service.get_smaller_than(
        column, value, n, order, species
    )
    return jsonify(iris_list)


@app.route("/iris/<column>/equal_to")
def get_equal_to(column):
    """
    Retrieve Iris rows where a column equals a value.

    Path Params:
        column (str): Column name.

    Query Params:
        value (float): Value to match (required).
        n (int): Max number of rows (optional).
        species (str): Filter by species (optional).

    Returns:
        200 OK: List of Iris records as JSON.
        400 Bad Request: If parameters are invalid.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    try:
        species = request.args.get("species")
        value = float(request.args.get("value"))
        n = request.args.get("n", type=int)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid value parameter"}), 400

    iris_list = app.iris_service.get_equal_to(column, value, n, species)
    return jsonify(iris_list)


@app.route("/iris/<column>/top_n")
def get_n(column):
    """
    Retrieve the top N Iris rows ordered by a column.

    Path Params:
        column (str): Column name.

    Query Params:
        n (int): Number of rows to return (required).
        order (str): "asc" or "desc" (default: "asc").
        species (str): Filter by species (optional).

    Returns:
        200 OK: List of Iris records as JSON.
        400 Bad Request: If parameters are invalid or missing.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    n = request.args.get("n", type=int)
    order = request.args.get("order", "asc")
    if not n:
        return jsonify({"error": "Missing n parameter"}), 400

    iris_list = app.iris_service.get_n(column, n, order, species)
    return jsonify(iris_list)


@app.route("/iris/<column>/smallest")
def get_smallest(column):
    """
    Retrieve the smallest value in a column.

    Path Params:
        column (str): Column name.

    Query Params:
        species (str): Filter by species (optional).

    Returns:
        200 OK: Smallest value as JSON.
        400 Bad Request: If column is invalid.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    result = app.iris_service.get_smallest_value(column, species)
    return jsonify(result)


@app.route("/iris/<column>/largest")
def get_largest(column):
    """
    Retrieve the largest value in a column.

    Path Params:
        column (str): Column name.

    Query Params:
        species (str): Filter by species (optional).

    Returns:
        200 OK: Largest value as JSON.
        400 Bad Request: If column is invalid.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    result = app.iris_service.get_largest_value(column, species)
    return jsonify(result)


@app.route("/iris/<column>/average")
def get_average(column):
    """
    Retrieve the average value of a column.

    Path Params:
        column (str): Column name.

    Query Params:
        species (str): Filter by species (optional).

    Returns:
        200 OK: Average value as JSON.
        400 Bad Request: If column is invalid.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    result = app.iris_service.get_average_value(column, species)
    return jsonify(result)


@app.route("/iris/<column>/median")
def get_median(column):
    """
    Retrieve the median value of a column.

    Path Params:
        column (str): Column name.

    Query Params:
        species (str): Filter by species (optional).

    Returns:
        200 OK: Median value as JSON.
        400 Bad Request: If column is invalid.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    result = app.iris_service.get_median_value(column, species)
    return jsonify(result)


@app.route("/iris/<column>/quantile")
def get_quantile(column):
    """
    Retrieve a quantile value from a column.

    Path Params:
        column (str): Column name.

    Query Params:
        q (float): Quantile between 0 and 1 (required).
        species (str): Filter by species (optional).

    Returns:
        200 OK: Quantile value as JSON.
        400 Bad Request: If column is invalid or q is missing/invalid.
    """
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    q = request.args.get("q", type=float)
    species = request.args.get("species")

    if q is None or not 0 <= q <= 1:
        return jsonify({"error": "Query parameter 'q' must be between 0 and 1"}), 400

    result = app.iris_service.get_quantile_value(column, q, species)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
