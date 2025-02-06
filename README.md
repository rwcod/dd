# Image to Text Caption Generator

A Docker-based application that generates text captions for images using the BLIP model. The application retrieves image references from MongoDB, generates captions, and stores them back in the database.

## Architecture Overview
```
+---------------+         +--------------------+         +--------------------+
|    Images     |  --->   |  AI Model (I2T)   |  --->   |   MongoDB          |
| (Mongo Refs)  |         |   Dockerized      |  Text   | (Caption Storage)  |
+---------------+         +--------------------+         +--------------------+
       |                               ^
       |                               |
       |                       Docker Container
       |                               |
       +------------ Callback URL <----+
```

## Features
- MongoDB integration for image reference and model configuration retrieval
- BLIP model for high-quality image caption generation
- Optional callback notifications with detailed status
- GPU acceleration support
- Docker containerization for easy deployment
- Comprehensive error handling and logging
- Configurable model parameters via MongoDB

## Prerequisites
- Docker installed on your system
- MongoDB instance with image references
- (Optional) NVIDIA GPU with CUDA support
- (Optional) Endpoint for callback notifications

## MongoDB Schema

### Images Collection
Documents should contain:
- `_id`: Unique identifier for the image
- `path`: Path or URL to the image
- `dataset_id` (optional): Identifier for grouping images
- `caption` (will be added): Generated caption
- `confidence` (will be added): Model confidence score
- `processed_at` (will be added): Timestamp of processing

### Model Configurations Collection
Documents can contain:
- `_id`: Configuration identifier
- `model_name`: Hugging Face model name
- `use_gpu`: Boolean for GPU usage
- `batch_size`: Processing batch size
- `is_default`: Boolean to mark default configuration

## Building the Docker Image

### CPU Version
```bash
docker build -t img2text .
```

### GPU Version
```bash
docker build -t img2text --build-arg USE_GPU=1 .
```

## Running the Container

### Basic Usage
```bash
docker run img2text --mongo_uri "mongodb://username:password@host:port/database"
```

### With All Options
```bash
docker run img2text \
    --mongo_uri "mongodb://username:password@host:port/database" \
    --dataset_id "your-dataset-id" \
    --model_config_id "your-config-id" \
    --callback_url "http://your-callback-url"
```

### With GPU Support
```bash
docker run --gpus all img2text \
    --mongo_uri "mongodb://username:password@host:port/database"
```

## Command Line Arguments
- `--mongo_uri` (required): MongoDB connection string
- `--dataset_id` (optional): Process specific dataset of images
- `--model_config_id` (optional): Use specific model configuration
- `--callback_url` (optional): Webhook for completion notification

## Environment Variables
You can use environment variables instead of command-line arguments:
```bash
docker run \
    -e MONGO_URI="mongodb://username:password@host:port/database" \
    -e DATASET_ID="your-dataset-id" \
    -e MODEL_CONFIG_ID="your-config-id" \
    -e CALLBACK_URL="http://your-callback-url" \
    img2text
```

## Project Structure
```
.
├── main.py           # Main application script
├── requirements.txt  # Python dependencies
├── Dockerfile       # Container configuration
└── README.md       # This documentation
```

## Components

### 1. MongoDB Handler
- Manages database connections
- Retrieves image references
- Stores generated captions
- Handles model configurations

### 2. Image Processor
- Loads and configures BLIP model
- Processes images for inference
- Generates text captions
- Handles GPU acceleration

### 3. Callback System
- Sends completion notifications
- Reports processing status
- Provides detailed results
- Handles error notifications

## Error Handling
The application provides comprehensive error handling for:
- MongoDB connection issues
- Image loading failures
- Model inference errors
- Callback notification failures
- Configuration retrieval issues

## Logging
Detailed logging includes:
- MongoDB connection status
- Model configuration loading
- GPU/CPU usage and capabilities
- Image processing progress
- Caption generation results
- Error messages and stack traces
- Callback notification status

## Performance Considerations
- Automatic GPU acceleration when available
- Configurable model parameters
- Batch processing capabilities
- Progress tracking with ETA
- Resource optimization options

## Security Notes
- Store sensitive credentials in environment variables
- Use secure MongoDB connections
- Restrict container network access
- Validate input data

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request