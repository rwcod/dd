# Cline Coder Instructions

This document details the recommended approach for the **Coder** role, focusing on the implementation of the Docker environment, database interactions, AI inference, and optional callbacks for the Dockerized AI Text-to-Image project.

---

## 1. Python Script Structure

1. **Argument Parsing**:
   - Use Python’s `argparse` to accept:
     - `--mongo_uri` (MongoDB connection string)
     - `--callback_url` (optional)
   - Additional arguments (e.g., `--dataset_id`, `--model_config_id`) can be included as needed.

2. **Database Interaction**:
   - Use `pymongo` to connect to MongoDB.
   - Query dataset collection and model configuration collection.
   - Insert results back into MongoDB for completed records.

3. **Model Inference**:
   - Load the pretrained Text-to-Image model (Stable Diffusion or alternative).
   - Generate images from text prompts.

4. **Image Storage**:
   - Use `google-cloud-storage` to upload generated images to GCS.
   - Store GCS URLs in MongoDB.

5. **Callback Notification**:
   - If a callback URL is provided, send a POST request with JSON results.

6. **Logging & Error Handling**:
   - Use `logging` to track process flow.
   - Wrap critical operations in `try/except` to capture errors.

---

## 2. Dockerfile Example

Below is a sample Dockerfile blueprint:

```
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Expose ports if needed
# EXPOSE 8080

# Define entrypoint
ENTRYPOINT ["python", "main.py"]
```

---

## 3. Requirements File

A typical `requirements.txt` might include:

```
pymongo
google-cloud-storage
torch
transformers
accelerate
diffusers
```

Adjust according to your chosen libraries.

---

## 4. Sample Code Snippet

```python
import argparse
import pymongo
import requests
from google.cloud import storage
from diffusers import StableDiffusionPipeline
import torch

# 1. Argument parsing
parser = argparse.ArgumentParser(description="Text-to-Image generation")
parser.add_argument("--mongo_uri", required=True, help="MongoDB connection URI")
parser.add_argument("--callback_url", required=False, help="Callback URL")
args = parser.parse_args()

# 2. Connect to MongoDB
client = pymongo.MongoClient(args.mongo_uri)
db = client["my_database"]

# 3. Retrieve dataset and model config
dataset = list(db.datasets.find({"status": "pending"}))
model_config = db.model_configs.find_one({"model_type": "stable_diffusion"})

# 4. Load Stable Diffusion model
pipeline = StableDiffusionPipeline.from_pretrained(model_config["model_path"], torch_dtype=torch.float16)
pipeline.to("cuda")  # if GPU available

# 5. Process dataset records
results = []
storage_client = storage.Client()
bucket = storage_client.bucket("my_gcs_bucket")

for record in dataset:
    text_prompt = record["text"]
    image = pipeline(text_prompt)["sample"][0]

    # Save image locally
    local_image_path = f"output_{record['_id']}.png"
    image.save(local_image_path)

    # Upload to GCS
    blob = bucket.blob(f"generated/{record['_id']}.png")
    blob.upload_from_filename(local_image_path)
    gcs_url = f"gs://{bucket.name}/{blob.name}"

    # Update MongoDB
    db.dataset_records.insert_one({
        "dataset_id": record["_id"],
        "prompt": text_prompt,
        "gcs_url": gcs_url,
        "status": "completed"
    })
    results.append({"record_id": record["_id"], "gcs_url": gcs_url})

# 6. Callback notification
if args.callback_url:
    requests.post(args.callback_url, json={"results": results})

print("Processing completed.")
```

---

## 5. Testing & Validation

1. **Local Testing**: Verify with a test MongoDB instance and local environment.
2. **Docker Build & Run**:
   - `docker build -t text2img:latest .`
   - `docker run --rm text2img:latest --mongo_uri <...> --callback_url <...>`
3. **Integration Testing**: Check end-to-end flow with actual services (MongoDB, GCS).
4. **Load Testing**: Ensure performance is adequate for larger datasets.

