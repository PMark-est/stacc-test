import os
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from src.models import Iris, Species, Base


def calculate_iris_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate additional features for the Iris dataset.
    """
    df['sepal_area'] = df['sepal_length'] * df['sepal_width']
    df['petal_area'] = df['petal_length'] * df['petal_width']
    df['sepal_to_petal_area_ratio'] = round(
        df['sepal_area'] / df['petal_area'], 2)
    df['sepal_to_petal_length_ratio'] = round(
        df['sepal_length'] / df['petal_length'], 2)
    df['sepal_to_petal_width_ratio'] = round(
        df['sepal_width'] / df['petal_width'], 2)
    return df


def load_iris_to_db(session: Session, csv_path: str = "iris.csv"):
    """
    Load the Iris dataset from CSV into the database.
    Computes additional features and ensures species are properly linked.
    """
    df = pd.read_csv(csv_path)

    # Compute additional derived features
    df = calculate_iris_features(df)

    # Create Species objects for unique species in the dataset
    species_objs = {name: Species(name=name)
                    for name in df["species"].unique()}
    session.add_all(species_objs.values())
    session.flush()  # Flush to assign IDs without committing

    # Create Iris objects for each row and link to Species
    iris_records = [
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
            species=species_objs[row["species"]],
        )
        for _, row in df.iterrows()
    ]
    session.add_all(iris_records)
    session.commit()


def wait_for_engine(max_retries: int = 30, retry_delay: int = 2):
    """
    Wait until the database is available before returning an engine.
    """
    database_url = os.getenv(
        'DATABASE_URL', 'postgresql://postgres:postgres@db:5432/irisdb'
    )

    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                print("✅ Database connection successful!")
                return engine
        except OperationalError as e:
            print(
                f"⏳ Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(retry_delay)

    # If all retries fail, raise an error
    raise OperationalError(
        "Could not connect to database after multiple attempts")


def get_engine():
    engine = wait_for_engine()
    Base.metadata.create_all(bind=engine)
    return engine


def get_session(engine):
    return Session(engine)


def seed_if_empty(session):
    if session.query(Iris).first() is None:
        load_iris_to_db(session)

