import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration settings for the Image-to-Text service."""
    
    # MongoDB settings
    mongo_uri: str
    
    # Model settings
    model_name: str = "Salesforce/blip-image-captioning-base"
    batch_size: int = 10
    use_gpu: bool = True
    
    # Optional settings
    dataset_id: Optional[str] = None
    callback_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        return cls(
            mongo_uri=os.getenv('MONGO_URI'),
            model_name=os.getenv('MODEL_NAME', cls.model_name),
            batch_size=int(os.getenv('BATCH_SIZE', cls.batch_size)),
            use_gpu=os.getenv('USE_GPU', 'true').lower() == 'true',
            dataset_id=os.getenv('DATASET_ID'),
            callback_url=os.getenv('CALLBACK_URL')
        )
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.mongo_uri:
            raise ValueError("MongoDB URI is required")
            
        if self.batch_size < 1:
            raise ValueError("Batch size must be positive")