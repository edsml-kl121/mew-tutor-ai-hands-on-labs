FROM python:3.11-slim

ENV POETRY_VERSION=2.1.4 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR
COPY src/ ./src/
COPY tests/ ./tests/
COPY src/project1/main.py ./

# TEMPORARILY COMMENT OUT THESE LINES:
# RUN useradd --create-home --shell /bin/bash app \
#     && chown -R app:app /app
# USER app

CMD ["poetry", "run", "python", "main.py"]