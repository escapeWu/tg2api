FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY app/ ./app/
COPY subscribers/ ./subscribers/
COPY main.py ./

# Create logs directory
RUN mkdir -p logs

EXPOSE 8101

CMD ["uv", "run", "python", "main.py"]
