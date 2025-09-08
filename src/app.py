from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from repositories import SpeciesRepository
from models.base import Base

def wait_for_db(max_retries=30, retry_delay=2):
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/irisdb')
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                print("✅ Database connection successful!")
                return engine
        except OperationalError as e:
            print(f"⏳ Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    
    raise OperationalError("Could not connect to database after multiple attempts")

app = Flask(__name__)
engine = wait_for_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

session = SessionLocal()
species_repo = SpeciesRepository(session)

@app.route("/species")
def get_species():
    result = species_repo.get_all()
    species_list = [{"id": species.id, "name": species.name} for species in result]
    return jsonify(species_list)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")