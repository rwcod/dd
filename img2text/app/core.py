import logging
from datetime import datetime
from typing import Dict, Any

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import pymongo
import requests

from .config import Config
from .utils import setup_logging

logger = logging.getLogger(__name__)

class ImageCaptioner:
    """Core class for image captioning functionality."""
    
    def __init__(self, config: Config):
        """Initialize the image captioning service.
        
        Args:
            config: Configuration settings
        """
        self.config = config
        setup_logging()
        
        # Initialize MongoDB
        self.client = pymongo.MongoClient(config.mongo_uri)
        self.db = self.client.get_default_database()
        
        # Initialize AI model
        logger.info(f"Loading model: {config.model_name}")
        self.processor = BlipProcessor.from_pretrained(config.model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(config.model_name)
        
        # Use GPU if available and configured
        if config.use_gpu and torch.cuda.is_available():
            logger.info("Using GPU for inference")
            self.model.to("cuda")
        else:
            logger.info("Using CPU for inference")
    
    def process_image(self, image_path: str) -> str:
        """Generate caption for a single image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Generated caption text
        
        Raises:
            Exception: If image processing fails
        """
        try:
            # Load and process image
            image = Image.open(image_path)
            inputs = self.processor(image, return_tensors="pt")
            
            # Move inputs to GPU if available and configured
            if self.config.use_gpu and torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate caption
            outputs = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            raise
    
    def process_dataset(self) -> None:
        """Process all pending images in the dataset."""
        # Build query
        query = {"status": "pending"}
        if self.config.dataset_id:
            query["dataset_id"] = self.config.dataset_id
        
        try:
            # Find pending images
            images = self.db.images.find(query)
            
            for image in images:
                try:
                    # Generate caption
                    caption = self.process_image(image["path"])
                    
                    # Update MongoDB
                    self._update_image_status(
                        image["_id"],
                        status="completed",
                        caption=caption
                    )
                    
                    # Send callback if configured
                    if self.config.callback_url:
                        self._send_callback({
                            "prompt_id": str(image["_id"]),
                            "image_path": image["path"],
                            "caption": caption
                        })
                    
                    logger.info(f"Successfully processed image: {image['path']}")
                    
                except Exception as e:
                    # Log error and update status
                    logger.error(f"Error processing image {image['path']}: {str(e)}")
                    self._update_image_status(
                        image["_id"],
                        status="error",
                        error=str(e)
                    )
                    
        except Exception as e:
            logger.error(f"Error accessing MongoDB: {str(e)}")
            raise
    
    def _update_image_status(self, image_id: str, status: str, **kwargs) -> None:
        """Update the status and metadata of an image in MongoDB.
        
        Args:
            image_id: MongoDB ID of the image
            status: New status to set
            **kwargs: Additional fields to update
        """
        update_data = {
            "status": status,
            f"{status}_at": datetime.utcnow(),
            **kwargs
        }
        
        self.db.images.update_one(
            {"_id": image_id},
            {"$set": update_data}
        )
    
    def _send_callback(self, data: Dict[str, Any]) -> None:
        """Send callback notification.
        
        Args:
            data: Data to send in the callback
        """
        try:
            response = requests.post(
                self.config.callback_url,
                json={"results": [data]},
                timeout=10
            )
            response.raise_for_status()
            logger.info("Callback sent successfully")
        except Exception as e:
            logger.error(f"Callback failed: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup."""
        if self.client:
            self.client.close()