from flask import Flask, jsonify, request, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from src.repositories import SpeciesRepository, IrisRepository
from src.services import SpeciesService, IrisService
from src.db import get_session, get_engine

app = Flask(__name__)
CORS(app, supports_credentials=True)

engine = get_engine()
db = get_session(engine)

# Initialize repositories and services
species_repo = SpeciesRepository(db)
iris_repo = IrisRepository(db)
app.species_service = SpeciesService(species_repo)
app.iris_service = IrisService(iris_repo)


@app.route("/spec.yaml")
def spec():
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
    try:
        species_name = request.json['species_name']
        sepal_length = float(request.json['sepal_length'])
        sepal_width = float(request.json['sepal_width'])
        petal_length = float(request.json['petal_length'])
        petal_width = float(request.json['petal_width'])

        # Call service
        iris = app.iris_service.create_iris(
            species_name, sepal_length, sepal_width, petal_length, petal_width)

        # Return JSON-serializable dict
        return jsonify(iris.to_dict()), 201

    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"error": "Invalid input data"}), 400


@app.route("/species")
def get_species():
    species_list = app.species_service.get_all_species()
    return jsonify(species_list)


@app.route("/iris/columns")
def get_columns():
    columns = app.iris_service.get_available_columns()
    return jsonify(columns)


@app.route("/iris/<name>")
def get_all_by_species(name):
    iris_list = app.iris_service.get_all_by_species(name)
    return jsonify(iris_list)


@app.route("/iris/<column>/larger_than")
def get_larger_than(column):
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    try:
        value = float(request.args.get("value"))
        n = request.args.get("n", type=int)  # Optional limit
        order = request.args.get("order", "asc")
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid value parameter"}), 400

    iris_list = app.iris_service.get_larger_than(column, value, n, order)
    return jsonify(iris_list)


@app.route("/iris/<column>/smaller_than")
def get_smaller_than(column):
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    try:
        value = float(request.args.get("value"))
        n = request.args.get("n", type=int)
        order = request.args.get("order", "asc")
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid value parameter"}), 400

    iris_list = app.iris_service.get_smaller_than(column, value, n, order)
    return jsonify(iris_list)


@app.route("/iris/<column>/equal_to")
def get_equal_to(column):
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
def get_top_n(column):
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    n = request.args.get("n", type=int)
    order = request.args.get("order", "asc")
    if not n:
        return jsonify({"error": "Missing n parameter"}), 400

    iris_list = app.iris_service.get_top_n(column, n, order, species)
    return jsonify(iris_list)


@app.route("/iris/<column>/smallest")
def get_smallest(column):
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    result = app.iris_service.get_smallest_value(column, species)
    return jsonify(result)


@app.route("/iris/<column>/largest")
def get_largest(column):
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    result = app.iris_service.get_largest_value(column, species)
    return jsonify(result)


@app.route("/iris/<column>/average")
def get_average(column):
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    result = app.iris_service.get_average_value(column, species)
    return jsonify(result)


@app.route("/iris/<column>/median")
def get_median(column):
    if not app.iris_service.validate_column(column):
        return jsonify({"error": "Invalid column"}), 400

    species = request.args.get("species")
    result = app.iris_service.get_median_value(column, species)
    return jsonify(result)


@app.route("/iris/<column>/quantile")
def get_quantile(column):
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
