# Text-to-Image Generation Service

A production-ready service that processes text prompts from MongoDB, generates images using Stable Diffusion, and stores them in Google Cloud Storage.

## Features

- Modular architecture with clean separation of concerns
- Async processing for better performance
- MongoDB integration for data storage
- Google Cloud Storage for image hosting
- Stable Diffusion for image generation
- Optional webhook callbacks
- Comprehensive error handling and logging
- GPU acceleration support
- Docker containerization
- Unit tests and type hints

## Project Structure

```
text2img/
├── app/
│   ├── __init__.py      # Package exports
│   ├── config.py        # Configuration management
│   ├── core.py          # Main generation logic
│   ├── storage.py       # GCS operations
│   └── utils.py         # Shared utilities
├── tests/
│   ├── __init__.py
│   └── test_core.py     # Unit tests
├── main.py              # CLI entry point
├── requirements.txt     # Dependencies
├── Dockerfile          # Container configuration
└── README.md          # Documentation
```

## Prerequisites

1. Python 3.10+
2. MongoDB instance
3. Google Cloud Storage bucket and credentials
4. Docker with NVIDIA Container Toolkit (for GPU support)

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd text2img
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Google Cloud Credentials**
   - Download your GCS service account key
   - Save it as `credentials/gcp-key.json`

## Usage

### Direct Python Usage

```bash
python main.py \
  --mongo-uri="mongodb://localhost:27017/dbname" \
  --gcs-bucket="your-bucket-name" \
  [--callback-url="http://your-callback-url"] \
  [--log-file="logs/generation.log"] \
  [--log-level="INFO"]
```

### Docker Usage

1. **Build Container**
   ```bash
   docker build -t text2img .
   ```

2. **Run Container**
   ```bash
   docker run --gpus all \
     -v $PWD/credentials:/app/credentials \
     -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json \
     text2img \
     --mongo-uri="mongodb://host.docker.internal:27017/dbname" \
     --gcs-bucket="your-bucket-name"
   ```

## MongoDB Document Format

### Input Document
```json
{
  "text": "A beautiful sunset over mountains",
  "status": "pending"
}
```

### Processed Document
```json
{
  "text": "A beautiful sunset over mountains",
  "status": "completed",
  "image_url": "gs://your-bucket/generated/123.png",
  "completed_at": "2025-02-05T18:30:00Z"
}
```

### Error Document
```json
{
  "text": "A beautiful sunset over mountains",
  "status": "error",
  "error": "Error message here",
  "error_at": "2025-02-05T18:30:00Z"
}
```

## Callback Format

When enabled, sends a POST request with:
```json
{
  "results": [
    {
      "prompt_id": "123",
      "prompt": "A beautiful sunset over mountains",
      "image_url": "gs://your-bucket/generated/123.png"
    }
  ]
}
```

## Development

1. **Run Tests**
   ```bash
   python -m pytest -v
   ```

2. **Type Checking**
   ```bash
   mypy app
   ```

## Configuration Options

| Parameter | Environment Variable | Description | Default |
|-----------|-------------------|-------------|---------|
| mongo_uri | MONGO_URI | MongoDB connection URI | Required |
| gcs_bucket | GCS_BUCKET | Google Cloud Storage bucket | Required |
| callback_url | CALLBACK_URL | Webhook URL | None |
| model_id | MODEL_ID | Stable Diffusion model | runwayml/stable-diffusion-v1-5 |
| num_inference_steps | NUM_INFERENCE_STEPS | Generation quality | 50 |
| batch_size | BATCH_SIZE | Max prompts per batch | 10 |

## Error Handling

- Failed generations are marked in MongoDB
- Full error logging with stack traces
- Automatic cleanup of resources
- Batch processing continues despite individual failures

## Performance

- Async processing for better throughput
- GPU acceleration when available
- Batch size configuration
- Connection pooling for MongoDB
- GCS upload optimization

## License

MIT License