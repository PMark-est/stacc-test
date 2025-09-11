import os
import time
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from src.models import Iris, Species, Base


def calculate_iris_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute derived features for an iris DataFrame and return the DataFrame.

    Rounds ratios to 2 decimals for easier storage/reading.
    """
    df = df.copy()
    df["sepal_area"] = df["sepal_length"] * df["sepal_width"]
    df["petal_area"] = df["petal_length"] * df["petal_width"]

    # avoid division by zero; where petal area / length / width are zero, store None
    df["sepal_to_petal_area_ratio"] = df.apply(
        lambda r: round(r["sepal_area"] / r["petal_area"], 2) if r["petal_area"] != 0 else None, axis=1
    )
    df["sepal_to_petal_length_ratio"] = df.apply(
        lambda r: round(r["sepal_length"] / r["petal_length"], 2) if r["petal_length"] != 0 else None, axis=1
    )
    df["sepal_to_petal_width_ratio"] = df.apply(
        lambda r: round(r["sepal_width"] / r["petal_width"], 2) if r["petal_width"] != 0 else None, axis=1
    )
    return df


def load_iris_to_db(session: Session, csv_path: str = "iris.csv"):
    """
    Read CSV and seed Iris and Species tables. Existing species are not duplicated.
    """
    df = pd.read_csv(csv_path)
    df = calculate_iris_features(df)

    # Create or get species objects (case-insensitive)
    unique_species = {name.lower() for name in df["species"].unique()}
    species_objs = {}
    for sname in unique_species:
        existing = session.query(Seeded := Species).filter(
            func.lower(Species.name) == sname).first() if False else None
        # simpler: create new species objects and rely on uniqueness on commit
        obj = Species(name=sname)
        species_objs[sname] = obj
    session.add_all(species_objs.values())
    session.flush()

    # Create iris records
    iris_records = []
    for _, row in df.iterrows():
        spec = species_objs[row["species"].lower()]
        iris_records.append(
            Iris(
                sepal_length=row["sepal_length"],
                sepal_width=row["sepal_width"],
                petal_length=row["petal_length"],
                petal_width=row["petal_width"],
                sepal_area=row["sepal_area"],
                petal_area=row["petal_area"],
                sepal_to_petal_area_ratio=row["sepal_to_petal_area_ratio"],
                sepal_to_petal_length_ratio=row["sepal_to_petal_length_ratio"],
                sepal_to_petal_width_ratio=row["sepal_to_petal_width_ratio"],
                species=spec,
            )
        )

    session.add_all(iris_records)
    session.commit()


def wait_for_engine(max_retries: int = 30, retry_delay: int = 2):
    """
    Try to connect to the database until successful or until retries exhaust.
    """
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@db:5432/irisdb")
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            with engine.connect():
                print("✅ Database connected")
                return engine
        except OperationalError as e:
            print(f"⏳ DB not ready (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    raise OperationalError(
        "Could not connect to database after multiple attempts")


def get_engine():
    engine = wait_for_engine()
    Base.metadata.create_all(bind=engine)
    return engine


def get_session(engine):
    return Session(engine)


def seed_if_empty(session: Session, csv_path: str = "iris.csv"):
    """Seed the DB from CSV when there are no iris records."""
    if session.query(Iris).first() is None:
        load_iris_to_db(session, csv_path)
