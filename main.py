#!/usr/bin/env python3
import argparse
import logging
import sys
from typing import List, Optional, Dict
import requests
from pymongo import MongoClient
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MongoDBHandler:
    """Handles all MongoDB operations"""
    def __init__(self, mongo_uri: str):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(mongo_uri)
            # Ping the server to check connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_model_config(self, config_id: Optional[str] = None) -> Dict:
        """Retrieve model configuration from MongoDB"""
        try:
            collection = self.client.img2text.model_configs
            query = {"_id": config_id} if config_id else {"is_default": True}
            config = collection.find_one(query)
            
            if not config:
                if config_id:
                    logger.warning(f"Config {config_id} not found, using default configuration")
                return {
                    "model_name": "Salesforce/blip-image-captioning-base",
                    "use_gpu": torch.cuda.is_available(),
                    "batch_size": 1
                }
            return config
        except Exception as e:
            logger.error(f"Failed to retrieve model configuration: {e}")
            raise

    def get_images(self, dataset_id: Optional[str] = None) -> List[dict]:
        """Retrieve image references from MongoDB"""
        try:
            collection = self.client.img2text.images
            query = {}
            
            if dataset_id:
                query["dataset_id"] = dataset_id
            
            # Only get images without captions
            query["caption"] = {"$exists": False}
            
            images = list(collection.find(query))
            logger.info(f"Retrieved {len(images)} images for processing")
            return images
        except Exception as e:
            logger.error(f"Failed to retrieve images: {e}")
            raise

    def save_caption(self, image_id: str, caption: str, confidence: float = None) -> None:
        """Save generated caption back to MongoDB"""
        try:
            collection = self.client.img2text.images
            update_data = {
                "caption": caption,
                "processed_at": datetime.datetime.utcnow()
            }
            if confidence is not None:
                update_data["confidence"] = confidence

            collection.update_one(
                {"_id": image_id},
                {"$set": update_data}
            )
            logger.debug(f"Saved caption for image {image_id}")
        except Exception as e:
            logger.error(f"Failed to save caption for image {image_id}: {e}")
            raise

class ImageProcessor:
    """Handles image processing and caption generation"""
    def __init__(self, model_config: Dict):
        """Initialize the model based on configuration"""
        try:
            logger.info(f"Loading model: {model_config['model_name']}")
            self.processor = BlipProcessor.from_pretrained(model_config['model_name'])
            self.model = BlipForConditionalGeneration.from_pretrained(model_config['model_name'])
            
            self.use_gpu = model_config.get('use_gpu', torch.cuda.is_available())
            if self.use_gpu and torch.cuda.is_available():
                self.model.to("cuda")
                logger.info("Using GPU for inference")
                # Log GPU information
                logger.info(f"GPU Device: {torch.cuda.get_device_name(0)}")
                logger.info(f"Available GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**2:.0f}MB")
            else:
                if self.use_gpu and not torch.cuda.is_available():
                    logger.warning("GPU requested but not available, falling back to CPU")
                logger.info("Using CPU for inference")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise

    def generate_caption(self, image_path: str) -> tuple[str, float]:
        """Generate caption for a given image"""
        try:
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(image, return_tensors="pt")
            
            if self.use_gpu and torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            # Generate caption with confidence score
            outputs = self.model.generate(
                **inputs,
                max_length=50,
                num_return_sequences=1,
                output_scores=True,
                return_dict_in_generate=True
            )
            
            caption = self.processor.decode(outputs.sequences[0], skip_special_tokens=True)
            confidence = float(torch.mean(outputs.scores[0]).item())
            
            return caption, confidence
        except Exception as e:
            logger.error(f"Failed to generate caption for {image_path}: {e}")
            raise

class CallbackNotifier:
    """Handles callback notifications"""
    @staticmethod
    def send_notification(callback_url: str, status: str, message: str, details: Optional[Dict] = None) -> None:
        """Send callback notification"""
        if not callback_url:
            return

        try:
            payload = {
                "status": status,
                "message": message,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            if details:
                payload.update(details)

            response = requests.post(callback_url, json=payload)
            response.raise_for_status()
            logger.info(f"Callback notification sent successfully to {callback_url}")
        except Exception as e:
            logger.error(f"Failed to send callback notification: {e}")
            # Don't raise the error - callback failures shouldn't stop processing

def main(mongo_uri: str, dataset_id: Optional[str] = None, 
         model_config_id: Optional[str] = None, callback_url: Optional[str] = None):
    """Main execution flow"""
    try:
        # Initialize MongoDB handler
        mongo_handler = MongoDBHandler(mongo_uri)
        
        # Get model configuration
        model_config = mongo_handler.get_model_config(model_config_id)
        
        # Initialize image processor with configuration
        image_processor = ImageProcessor(model_config)
        
        # Get images that need processing
        images = mongo_handler.get_images(dataset_id)
        logger.info(f"Found {len(images)} images to process")

        # Process each image
        processed_count = 0
        error_count = 0
        
        for image in tqdm(images, desc="Processing images"):
            try:
                # Generate caption with confidence score
                caption, confidence = image_processor.generate_caption(image['path'])
                
                # Save caption with metadata
                mongo_handler.save_caption(image['_id'], caption, confidence)
                
                processed_count += 1
                logger.info(f"Successfully processed image {image['_id']}")
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to process image {image['_id']}: {e}")
                continue

        # Send completion notification with detailed status
        if callback_url:
            CallbackNotifier.send_notification(
                callback_url,
                "completed",
                f"Processed {processed_count} images ({error_count} errors)",
                {
                    "total_images": len(images),
                    "processed_count": processed_count,
                    "error_count": error_count,
                    "dataset_id": dataset_id,
                    "model_config_id": model_config_id
                }
            )

    except Exception as e:
        logger.error(f"Application error: {e}")
        if callback_url:
            CallbackNotifier.send_notification(
                callback_url,
                "error",
                f"Application error: {str(e)}"
            )
        sys.exit(1)

if __name__ == "__main__":
    import datetime  # Import here to avoid circular import

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Image to Text Caption Generator")
    parser.add_argument(
        "--mongo_uri",
        required=True,
        help="MongoDB connection URI"
    )
    parser.add_argument(
        "--dataset_id",
        help="Optional dataset ID to process specific image set"
    )
    parser.add_argument(
        "--model_config_id",
        help="Optional model configuration ID"
    )
    parser.add_argument(
        "--callback_url",
        help="Optional callback URL for completion notification"
    )

    args = parser.parse_args()
    main(args.mongo_uri, args.dataset_id, args.model_config_id, args.callback_url)