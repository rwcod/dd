# Cline Coder Instructions - Image-to-Text

This document details the recommended approach for the **Coder** role, focusing on the implementation of the Docker environment, database interactions, AI inference, and optional callbacks for the Dockerized AI Image-to-Text project.

---

## 1. Application Structure

1. **Core Package (`app/`)**:
   ```
   app/
   ├── __init__.py      # Package exports
   ├── config.py        # Configuration management
   ├── core.py         # Main image captioning logic
   └── utils.py        # Helper functions
   ```

2. **Module Responsibilities**:
   - `config.py`: Manages environment variables and settings
   - `core.py`: Handles image processing and caption generation
   - `utils.py`: Provides logging and helper functions

3. **Entry Point**:
   - `main.py`: CLI interface and application initialization
   
4. **Testing**:
   - `tests/`: Unit tests for all components

---

## 2. Implementation Details

### Configuration (config.py)
```python
@dataclass
class Config:
    mongo_uri: str
    model_name: str = "Salesforce/blip-image-captioning-base"
    batch_size: int = 10
    use_gpu: bool = True
    dataset_id: Optional[str] = None
    callback_url: Optional[str] = None
```

### Core Processing (core.py)
```python
class ImageCaptioner:
    def __init__(self, config: Config):
        self.config = config
        self._init_model()
        self._init_mongo()
    
    def process_dataset(self):
        # Process images from MongoDB
        # Update results
        # Send callbacks if configured
```

### Utility Functions (utils.py)
```python
def setup_logging(level: str = "INFO"):
    # Configure logging

def format_error(error: Exception) -> str:
    # Format error messages
```

---

## 3. MongoDB Integration

1. **Dataset Collection Schema**:
```json
{
    "_id": "ObjectId",
    "path": "string",       // Path to image
    "dataset_id": "string", // Optional grouping
    "status": "string",     // pending|completed|error
    "caption": "string",    // Generated caption
    "processed_at": "date"  // Timestamp
}
```

2. **Status Updates**:
   - Update document status as processing progresses
   - Include error details if processing fails
   - Track processing timestamps

---

## 4. Error Handling

1. **Graceful Failures**:
   - Catch and log exceptions
   - Update MongoDB with error status
   - Continue processing remaining images

2. **Common Error Cases**:
   - Image loading failures
   - Model inference errors
   - MongoDB connection issues
   - Callback failures

---

## 5. Testing Strategy

1. **Unit Tests**:
   - Mock MongoDB interactions
   - Mock model inference
   - Test configuration validation
   - Test error handling

2. **Integration Tests**:
   - Test with real MongoDB connection
   - Validate end-to-end workflow
   - Test callback functionality

---

## 6. Performance Considerations

1. **GPU Utilization**:
   - Check GPU availability
   - Move tensors to GPU when available
   - Optimize batch sizes

2. **Memory Management**:
   - Clear GPU memory after processing
   - Use connection pooling for MongoDB
   - Clean up resources properly

---

## 7. Logging Best Practices

1. **Log Levels**:
   - ERROR: Processing failures
   - INFO: Progress updates
   - DEBUG: Detailed operations

2. **Log Content**:
   - Include image identifiers
   - Log processing times
   - Track resource usage