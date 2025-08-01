# === Builder stage: install deps with cache ===
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps needed to build wheels (add gcc/musl if your deps need compiling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Only copy requirements to leverage Docker layer cache
COPY src/requirements.txt /app/requirements.txt
RUN pip wheel --wheel-dir /wheels -r /app/requirements.txt

# === Runtime stage: minimal image with postgres client ===
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install PostgreSQL client only in final image
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# Create working dir
RUN mkdir /app
WORKDIR /app

# Copy wheels and install
COPY --from=builder /wheels /wheels
COPY src/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r /app/requirements.txt

# Copy application source and config
COPY src/ /app/
COPY gunicorn.conf.py /app/gunicorn.conf.py
COPY entrypoint.sh /app/
COPY wait-for-it.sh /app/

# Expose port
EXPOSE 8000

# Make scripts executable
RUN chmod +x /app/wait-for-it.sh && chmod +x /app/entrypoint.sh

# Entrypoint
CMD ["/app/entrypoint.sh"]