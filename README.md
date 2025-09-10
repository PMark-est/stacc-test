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

1. Clone the repo:
   ```bash
   git clone git@github.com:PMark-est/stacc-test.git
   cd stacc-test
   ```
2. Run the image:
    ```bash
    docker compose up --build
    ```
