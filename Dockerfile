# Base image
ARG TIMEZONE="Europe/Lisbon"

FROM python:3.13.2-slim AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

# Builder stage
FROM base AS builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install necessary system packages and Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata curl && \
    ln -fs /usr/share/zoneinfo/${TIMEZONE} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir poetry

WORKDIR /skywizz

# Copy dependency files first for better layer caching
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-root

# Runtime stage
FROM python:3.13.2-slim AS runtime

ENV MPLCONFIGDIR="/skywizz/.config/matplotlib"

# Install necessary system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl tzdata && \
    ln -fs /usr/share/zoneinfo/${TIMEZONE} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-privileged user
RUN adduser --system --group --no-create-home skywizz

# Set work directory
WORKDIR /skywizz

# Copy only the virtual environment from builder to minimize image size
COPY --from=builder /skywizz/.venv ./.venv

# Copy the application code
COPY . .

# Set permissions
RUN mkdir ./images && \
    chown -R skywizz:0 /skywizz && \
    chmod -R g=u /skywizz && \
    chmod -R g+w /skywizz

# Switch to the non-privileged user
USER skywizz:0

# Update PATH to include the virtual environment
ENV PATH="/skywizz/.venv/bin:${PATH}" \
    VIRTUAL_ENV="/skywizz/.venv"

CMD ["python", "SkyWizz.py"]
