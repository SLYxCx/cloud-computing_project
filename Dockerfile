# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set metadata
LABEL maintainer="declan.dymond@gmail.com"
LABEL description="Nutritional Data Analysis Docker Container"
LABEL version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies required for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (for better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY data_analysis.py /app/
COPY All_Diets.csv /app/

# Create output directory for generated files
RUN mkdir -p /app/output

# Run the analysis script
CMD ["python", "data_analysis.py"]