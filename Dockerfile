FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY pyproject.toml poetry.lock /tmp

RUN poetry export --format requirements.txt --output requirements.txt --without-hashes

FROM python:3.10

WORKDIR /app

COPY author1zd /app/author1zd/
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["uvicorn", "author1zd.app:app", "--host", "0.0.0.0", "--port", "8000"]
