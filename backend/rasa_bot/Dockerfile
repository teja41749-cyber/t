FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Rasa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Rasa bot files
COPY . .

# Create models directory
RUN mkdir -p models

# Set environment variables
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5005

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5005/webhooks/rest/webhook || exit 1

# Run Rasa actions and API server
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--port", "5005"]