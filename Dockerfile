FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for cryptography package
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# MCP stdio server — does not bind a port
# Private key is mounted at runtime via volume or secret
CMD ["python", "main.py"]
