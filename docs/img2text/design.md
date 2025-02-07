# Project Design Document - Image to Text

## Core Structure
```
img2text/
├── app/
│   ├── __init__.py
│   ├── core.py          # Main business logic for image processing
│   ├── config.py        # Configuration and environment settings
│   └── utils.py         # Helper functions
├── tests/
│   ├── __init__.py
│   └── test_core.py     # Unit tests
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
└── main.py             # Entry point
```

## Key Design Decisions

1. **Minimal Dependencies**
   - torch + transformers: BLIP model for image captioning
   - pymongo: MongoDB interaction
   - python-dotenv: Environment management
   - requests: HTTP callbacks
   - Pillow: Image processing

2. **Configuration**
   - Environment variables for sensitive data
   - Simple config class for settings
   - Dataset and model configuration from MongoDB

3. **Core Features**
   - Single responsibility per module
   - Async processing for better performance
   - Error handling and logging
   - Clean interface between components
   - MongoDB integration for dataset management
   - Optional callback notifications

4. **Development Workflow**
   1. Set up project structure
   2. Implement core functionality
   3. Add tests
   4. Containerize
   5. Test end-to-end

## Key Components

1. **Image Caption Generator**
   - Uses BLIP model for high-quality image captions
   - GPU acceleration when available
   - Batch processing support

2. **Dataset Processing**
   - MongoDB integration for image references
   - Status tracking for each processed image
   - Error handling and recovery

3. **Configuration Management**
   - Environment-based settings
   - MongoDB-based model configuration
   - Runtime parameter support

4. **Testing & Quality**
   - Unit tests for core components
   - Integration tests for MongoDB
   - Mocked image processing for tests

## Implementation Details

1. **MongoDB Schema**
   ```json
   {
     "_id": "unique_id",
     "path": "path/to/image.jpg",
     "dataset_id": "optional_dataset_grouping",
     "status": "pending|completed|error",
     "caption": "Generated caption text",
     "processed_at": "ISO timestamp",
     "error": "Error message if failed"
   }
   ```

2. **Configuration Options**
   - MONGO_URI: MongoDB connection string
   - MODEL_NAME: BLIP model variant
   - USE_GPU: Enable GPU acceleration
   - BATCH_SIZE: Processing batch size
   - CALLBACK_URL: Optional webhook URL

3. **Error Handling**
   - Graceful failure handling
   - Detailed error logging
   - Status updates in MongoDB
   - Optional error callbacks

4. **Performance Optimization**
   - GPU acceleration when available
   - Batch processing of images
   - Connection pooling for MongoDB
   - Resource cleanup

## Next Steps

1. Implement monitoring and metrics
2. Add support for custom models
3. Implement batch size optimization
4. Add support for different caption models
5. Enhance error recovery mechanisms