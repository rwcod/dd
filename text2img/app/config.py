"""Configuration management for the text-to-image processor."""
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class Config:
    """Application configuration settings."""
    
    # MongoDB settings
    mongo_uri: str
    database_name: str
    collection_name: str = "prompts"
    
    # Google Cloud Storage settings
    gcs_bucket: str
    gcs_prefix: str = "generated"
    
    # Model settings
    model_id: str = "runwayml/stable-diffusion-v1-5"
    num_inference_steps: int = 50
    device: str = "cuda" if os.environ.get("USE_GPU", "true").lower() == "true" else "cpu"
    
    # Optional settings
    callback_url: Optional[str] = None
    callback_timeout: int = 10
    batch_size: int = 10
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        return cls(
            mongo_uri=os.environ["MONGO_URI"],
            database_name=os.environ.get("MONGO_DB", "text2img"),
            collection_name=os.environ.get("MONGO_COLLECTION", "prompts"),
            gcs_bucket=os.environ["GCS_BUCKET"],
            gcs_prefix=os.environ.get("GCS_PREFIX", "generated"),
            model_id=os.environ.get("MODEL_ID", "runwayml/stable-diffusion-v1-5"),
            callback_url=os.environ.get("CALLBACK_URL"),
            num_inference_steps=int(os.environ.get("NUM_INFERENCE_STEPS", "50")),
            batch_size=int(os.environ.get("BATCH_SIZE", "10"))
        )
    
    @classmethod
    def from_args(cls, mongo_uri: str, gcs_bucket: str, callback_url: Optional[str] = None) -> 'Config':
        """Create configuration from command line arguments."""
        return cls(
            mongo_uri=mongo_uri,
            database_name=mongo_uri.split("/")[-1],  # Extract DB name from URI
            gcs_bucket=gcs_bucket,
            callback_url=callback_url
        )
    
    def validate(self) -> None:
        """Validate the configuration settings."""
        if not self.mongo_uri:
            raise ValueError("MongoDB URI is required")
        if not self.gcs_bucket:
            raise ValueError("GCS bucket name is required")
        if self.num_inference_steps < 1:
            raise ValueError("num_inference_steps must be positive")
        if self.batch_size < 1:
            raise ValueError("batch_size must be positive")