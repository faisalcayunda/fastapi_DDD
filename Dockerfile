FROM python:3.13-slim-bookworm AS base

ENV POETRY_HOME="/opt/poetry" \
    PYTHONPATH=/app \
    PYTHONHASHSEED=0 \
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    PYTHONWRITEBYTECODE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    locales \
    locales-all \
    libmagic1 \
    libjemalloc2 \
    procps && \
    rm -rf /var/lib/apt/lists/* && \
    echo "id_ID.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

ENV LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libjemalloc.so.2"
ENV MALLOC_CONF="background_thread:true,metadata_thp:auto,dirty_decay_ms:30000,muzzy_decay_ms:30000"

FROM base AS builder

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 -

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-root --no-interaction --no-ansi

RUN apt-get autoremove -y && \
    apt-get purge -y curl git build-essential && \
    apt-get clean -y && \
    rm -rf /root/.cache /var/lib/apt/lists/*

FROM base AS app-image

COPY --from=builder /opt/poetry /opt/poetry
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY . /app

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONOPTIMIZE=2

EXPOSE 5000

CMD ["python", "-OO", "run.py"]
