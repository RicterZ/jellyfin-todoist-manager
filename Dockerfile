FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    $POETRY_HOME/bin/poetry --version

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Configure Poetry: Don't create virtual env, install dependencies globally
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" || exit 1

# Run the application
CMD ["python", "main.py"]

