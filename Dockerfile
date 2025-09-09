FROM python:3.12

WORKDIR /flask_app

COPY requirements.txt .
COPY iris.csv .
RUN pip install -r requirements.txt
COPY src/ src/
COPY tests/ tests/

CMD ["python3", "-m", "flask", "--app", "src/app", "run", "--host=0.0.0.0"] 