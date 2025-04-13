FROM --platform=$BUILDPLATFORM python:3.9-slim

WORKDIR /app

# Install build dependencies and runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the Prometheus metrics port
EXPOSE 8000

# Run the exporter
CMD ["python", "exporter.py"] 