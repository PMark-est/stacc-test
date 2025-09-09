from flask import Flask, jsonify
from repositories import SpeciesRepository


app = Flask(__name__)
species_repo = SpeciesRepository()


@app.route("/species")
def get_species():
    result = species_repo.get_all()
    species_list = [{"id": species.id, "name": species.name}
                    for species in result]
    return jsonify(species_list)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
