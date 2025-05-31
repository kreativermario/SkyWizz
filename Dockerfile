# Base image
FROM python:3.13.3-alpine3.22 AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

# Builder stage
FROM base AS builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Install system packages for building
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    musl-dev \
    py3-pip \
    curl \
    git

# Install Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /skywizz

# Copy dependency files first
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-root

# Runtime stage
FROM python:3.13.3-alpine3.22 AS runtime

ENV TIMEZONE="Europe/Lisbon"
ENV MPLCONFIGDIR="/skywizz/.config/matplotlib"

# Install runtime dependencies
RUN apk add --no-cache \
    curl \
    tzdata \
    su-exec \
    traceroute \
    libstdc++ && \
    cp /usr/share/zoneinfo/${TIMEZONE} /etc/localtime && \
    echo "${TIMEZONE}" > /etc/timezone

# Add non-root user
RUN addgroup -S skywizz && adduser -S -G skywizz skywizz

WORKDIR /skywizz

# Copy only the virtual environment from builder
COPY --from=builder /skywizz/.venv ./.venv

# Copy application code
COPY . .

# Create folders and fix permissions
RUN mkdir -p ./images && \
    chown -R skywizz:skywizz /skywizz && \
    chmod -R g=u /skywizz && \
    chmod -R g+w /skywizz

# Switch to non-privileged user
USER skywizz

# Set Python path
ENV PATH="/skywizz/.venv/bin:$PATH" \
    VIRTUAL_ENV="/skywizz/.venv"

CMD ["python", "SkyWizz.py"]
