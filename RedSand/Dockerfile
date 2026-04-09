# RedSand Secure - Base Image
FROM python:3.10-slim-bullseye

# Security: Run as non-root user
RUN groupadd -r redsand && useradd -r -g redsand redsand

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    pefile \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/reports /app/quarantine && \
    chown -R redsand:redsand /app

# Switch to non-root user
USER redsand

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    REDSAND_ENV=production \
    LOG_LEVEL=INFO \
    MAX_WORKERS=4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "redsand_secure.py", "--help"]
