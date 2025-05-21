FROM python:3.12.2-slim AS Builder

ENV C_FORCE_ROOT=True
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/code

WORKDIR /code

COPY poetry.lock pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY pyproject.toml /code/

FROM python:3.12.2-slim AS Runtime

WORKDIR /app

ENV C_FORCE_ROOT=True
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080

COPY --from=Builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=Builder /usr/local/bin/poetry /usr/local/bin/poetry
COPY --from=Builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY . .