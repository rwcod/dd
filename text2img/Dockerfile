# Use NVIDIA CUDA base image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY app/ app/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create volume mount points for credentials and logs
VOLUME ["/app/credentials", "/app/logs"]

# Default command
ENTRYPOINT ["python3", "main.py"]

# Usage Instructions:
# 1. Build:
#    docker build -t text2img .
#
# 2. Run with GPU:
#    docker run --gpus all \
#      -v $PWD/credentials:/app/credentials \
#      -v $PWD/logs:/app/logs \
#      -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json \
#      text2img \
#      --mongo-uri="mongodb://host.docker.internal:27017/dbname" \
#      --gcs-bucket="your-bucket-name" \
#      --log-file="/app/logs/generation.log" \
#      [--callback-url="http://your-callback-url"]
#
# 3. Run without GPU:
#    docker run \
#      -v $PWD/credentials:/app/credentials \
#      -v $PWD/logs:/app/logs \
#      -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json \
#      -e USE_GPU=false \
#      text2img \
#      --mongo-uri="mongodb://host.docker.internal:27017/dbname" \
#      --gcs-bucket="your-bucket-name" \
#      --log-file="/app/logs/generation.log" \
#      [--callback-url="http://your-callback-url"]