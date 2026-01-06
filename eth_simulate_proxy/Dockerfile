FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY proxy_service.py .

# Create non-root user
RUN useradd -m -u 1000 proxyuser && \
    chown -R proxyuser:proxyuser /app

# Switch to non-root user
USER proxyuser

# Expose port
EXPOSE 8545

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://127.0.0.1:8545/health')" || exit 1

# Run the application
CMD ["python", "proxy_service.py"]
