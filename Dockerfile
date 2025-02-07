# Use CUDA base image if GPU is available, otherwise use slim
ARG USE_GPU=0
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime AS gpu-base
FROM python:3.9-slim AS cpu-base

FROM ${USE_GPU:+gpu-base}${USE_GPU:-cpu-base}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .

# Make the script executable
RUN chmod +x main.py

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]