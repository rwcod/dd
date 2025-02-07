import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Optional

import pymongo
import requests
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageCaptioner:
    def __init__(self, mongo_uri: str, callback_url: Optional[str] = None):
        self.mongo_uri = mongo_uri
        self.callback_url = callback_url
        self.model_name = "Salesforce/blip-image-captioning-base"
        
        # Initialize MongoDB connection
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client.get_default_database()
        
        # Load AI model
        logger.info(f"Loading model: {self.model_name}")
        self.processor = BlipProcessor.from_pretrained(self.model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
        
        # Use GPU if available
        if torch.cuda.is_available():
            logger.info("Using GPU for inference")
            self.model.to("cuda")
        
    def process_image(self, image_path: str) -> str:
        """Generate caption for a single image."""
        try:
            # Load and process image
            image = Image.open(image_path)
            inputs = self.processor(image, return_tensors="pt")
            
            # Move inputs to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate caption
            outputs = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            raise
            
    def process_dataset(self, dataset_id: Optional[str] = None):
        """Process all images in the dataset."""
        # Build query
        query = {"status": "pending"}
        if dataset_id:
            query["dataset_id"] = dataset_id
            
        try:
            # Find pending images
            images = self.db.images.find(query)
            
            for image in images:
                try:
                    # Generate caption
                    caption = self.process_image(image["path"])
                    
                    # Update MongoDB
                    self.db.images.update_one(
                        {"_id": image["_id"]},
                        {
                            "$set": {
                                "caption": caption,
                                "status": "completed",
                                "processed_at": datetime.utcnow()
                            }
                        }
                    )
                    
                    # Send callback if configured
                    if self.callback_url:
                        self._send_callback({
                            "prompt_id": str(image["_id"]),
                            "image_path": image["path"],
                            "caption": caption
                        })
                        
                    logger.info(f"Successfully processed image: {image['path']}")
                    
                except Exception as e:
                    # Log error and update status
                    logger.error(f"Error processing image {image['path']}: {str(e)}")
                    self.db.images.update_one(
                        {"_id": image["_id"]},
                        {
                            "$set": {
                                "status": "error",
                                "error": str(e),
                                "error_at": datetime.utcnow()
                            }
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Error accessing MongoDB: {str(e)}")
            raise
            
    def _send_callback(self, data: dict):
        """Send callback notification."""
        try:
            response = requests.post(
                self.callback_url,
                json={"results": [data]},
                timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Callback failed: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Image to Text Caption Generator")
    parser.add_argument("--mongo_uri", required=True, help="MongoDB connection string")
    parser.add_argument("--dataset_id", help="Optional dataset ID to process")
    parser.add_argument("--callback_url", help="Optional callback URL")
    
    args = parser.parse_args()
    
    try:
        captioner = ImageCaptioner(
            mongo_uri=args.mongo_uri,
            callback_url=args.callback_url
        )
        captioner.process_dataset(args.dataset_id)
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()