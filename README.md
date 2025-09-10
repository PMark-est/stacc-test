# 🌸 Classic Iris API

A simple REST API for exploring the classic [Iris dataset](https://en.wikipedia.org/wiki/Iris_flower_data_set).  
This project wraps the dataset with a Dockerized Flask app, providing endpoints for querying, filtering, and performing basic statistics.

---

## ✨ Features
- 🔍 Query iris flowers by species or measurements
- 📊 Compute statistics (min, max, average, median, quantiles)
- ⚡ Fast responses via SQLAlchemy + Postgres
- 📖 Interactive API docs powered by Swagger UI

---

## 🛠️ Prerequisites
- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## 🚀 Running the API
By default the container runs on port 5000, but this can be configured in the docker-compose.yml\
👉 Swagger docs available at: http://localhost:5000/docs


1. Clone the repo:
   ```bash
   git clone git@github.com:PMark-est/stacc-test.git
   cd stacc-test
   ```
2. Run the image:
    ```bash
    docker compose up --build
    ```

## Linting and formatting

To get linting and autoformatting based on pep8 specifications in VSCode install the following addons:\
- Pylint
- autopep8

## Running tests

To run tests execute the command
```bash
docker compose --profile test up --build --exit-code-from tests
```
