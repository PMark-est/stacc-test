from flask import Flask, jsonify, request, send_from_directory, abort, Response, json
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from src.repositories import SpeciesRepository, IrisRepository
from src.services import SpeciesService, IrisService
from src.db import get_session, get_engine, seed_if_empty
import typing as t

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Initialize DB and services on import (same behaviour as before)
engine = get_engine()
db_session = get_session(engine)
seed_if_empty(db_session)

species_repo = SpeciesRepository(db_session)
iris_repo = IrisRepository(db_session)
app.species_service = SpeciesService(species_repo)
app.iris_service = IrisService(iris_repo)


@app.route("/spec.yaml")
def spec():
    """Serve OpenAPI spec file."""
    return send_from_directory(".", "spec.yaml")


# Swagger UI
SWAGGER_URL = "/docs"
API_URL = "/spec.yaml"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Iris API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# --- Iris endpoints ----------------------------------------------------

@app.route("/irises", methods=["GET"])
def list_irises():
    """
    List irises with optional filters:
      - species, min_<field>, max_<field>, sort_by, sort_order, limit
    """
    try:
        params = request.args.to_dict()
        irises = app.iris_service.list_irises(params)
        return jsonify(irises)
    except ValueError as e:
        response = app.response_class(
            response=json.dumps(str(e)),
            status=400,
            mimetype='application/json'
        )
        return response


@app.route("/irises", methods=["POST"])
def create_iris():
    """
    Create an iris. Expected JSON body:
    {
      "species_name": str,
      "sepal_length": float,
      "sepal_width": float,
      "petal_length": float,
      "petal_width": float
    }
    """
    body = request.get_json(silent=True)
    if not body:
        response = app.response_class(
            response=json.dumps("no body"),
            status=400,
            mimetype='application/json'
        )
        return response

    try:
        species_name = body["species_name"]
        sepal_length = float(body["sepal_length"])
        sepal_width = float(body["sepal_width"])
        petal_length = float(body["petal_length"])
        petal_width = float(body["petal_width"])
    except (KeyError, TypeError, ValueError) as e:
        response = app.response_class(
            response=json.dumps(str(e)),
            status=400,
            mimetype='application/json'
        )
        return response

    try:
        iris = app.iris_service.create_iris(
            species_name, sepal_length, sepal_width, petal_length, petal_width)
        response = app.response_class(
            response=json.dumps(iris),
            status=201,
            mimetype='application/json'
        )
        return response
    except Exception:
        abort(500)


@app.route("/irises/<int:iris_id>", methods=["GET"])
def get_iris(iris_id: int):
    """Get a single iris by id."""
    iris = app.iris_service.get_iris_by_id(iris_id)
    if iris is None:
        abort(404)
    return jsonify(iris)


@app.route("/irises/<int:iris_id>", methods=["PUT"])
def update_iris(iris_id: int):
    """Update an iris by id."""
    body = request.get_json(silent=True)
    if body is None:
        response = app.response_class(
            response=json.dumps("no body"),
            status=400,
            mimetype='application/json'
        )
        return response
    try:
        updated = app.iris_service.update_iris(iris_id, body)
    except ValueError as e:
        response = app.response_class(
            response=json.dumps(str(e)),
            status=400,
            mimetype='application/json'
        )
        return response

    if updated is None:
        abort(404)
    return jsonify(updated)


@app.route("/irises/<int:iris_id>", methods=["DELETE"])
def delete_iris(iris_id: int):
    """Delete an iris by id."""
    deleted = app.iris_service.delete_iris_by_id(iris_id)
    if not deleted:
        abort(404)
    return jsonify({"status": "success", "message": f"Iris {iris_id} deleted"})

    # --- Species endpoints ------------------------------------------------


@app.route("/species", methods=["GET"])
def list_species():
    """Return all species."""
    species_list = app.species_service.get_all_species()
    return jsonify(species_list)


@app.route("/species/<string:species_name>/summary", methods=["GET"])
def species_summary(species_name: str):
    """Return measurement summary for a species."""
    summary = app.iris_service.get_summary_for_species(species_name)
    return jsonify(summary)


@app.route("/statistics", methods=["GET"])
def statistics():
    """Return dataset wide statistics and species distribution."""
    stats = app.iris_service.get_stats_for_species(app.species_service)
    return jsonify(stats)


@app.route("/statistics/quantile", methods=["GET"])
def statistics_quantile():
    """
    Compute a quantile for a given measurement column.

    Query params:
      - measurement: str (required, e.g. "sepal_length")
      - quantile: float between 0 and 1 (required)
      - species: str (optional, case-insensitive)
    """
    try:
        measurement = request.args.get("measurement")
        q = float(request.args.get("quantile", ""))
        species = request.args.get("species_name")
    except (TypeError, ValueError) as e:
        response = app.response_class(
            response=json.dumps(str(e)),
            status=400,
            mimetype='application/json'
        )
        return response

    try:
        result = app.iris_service.get_quantile(measurement, q, species)
    except ValueError as e:
        response = app.response_class(
            response=json.dumps(str(e)),
            status=400,
            mimetype='application/json'
        )
        return response

    if result is None:
        abort(404)
    return jsonify({"measurement": measurement, "quantile": q, "species_name": species, "value": result})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
