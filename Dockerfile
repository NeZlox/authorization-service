# ====== Builder Stage ======
# Base image with build tools
FROM python:3.12.4-slim-bullseye AS builder

# Install system dependencies for building
RUN apt-get update  \
    && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Configure Poetry installation
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION="1.8.3" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR="/cache/poetry"
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry --version

# Install project dependencies
WORKDIR /app
COPY pyproject.toml ./
RUN poetry install --only main --no-root --no-interaction

# ====== Runner Stage ======
# Final lightweight image
FROM python:3.12.4-slim-bullseye AS runner

# Install minimal tools needed to run the app, such as curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends  \
    curl  \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set up Poetry in the runner image
ENV POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:/usr/local/bin:${PATH}"

# Copy artifacts from builder
COPY --from=builder ${POETRY_HOME} ${POETRY_HOME}
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app
WORKDIR /app

# Make the entry script executable
RUN chmod 777 /app/scripts/entry

# Use the entry script as the container's entry point
ENTRYPOINT ["/bin/bash", "/app/scripts/entry"]
