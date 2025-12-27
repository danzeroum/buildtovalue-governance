# BuildToValue v0.9 - Production Dockerfile
# Multi-stage build for security and size optimization

# === STAGE 1: Builder ===
FROM python:3.11-slim AS builder

# Metadata
LABEL maintainer="BuildToValue Team <dev@buildtovalue.com>"
LABEL version="0.9.0"
LABEL description="Enterprise AI Governance Framework - ISO 42001 Compliant"

# Build arguments
ARG ENVIRONMENT=production

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# === STAGE 2: Runtime ===
FROM python:3.11-slim

# Create non-root user (security best practice)
RUN useradd -m -u 1000 btv && \
    mkdir -p /app /app/data /app/logs /app/secrets && \
    chown -R btv:btv /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY --chown=btv:btv src/ /app/src/
COPY --chown=btv:btv scripts/ /app/scripts/

# Switch to non-root user
USER btv

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.interface.api.gateway:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
