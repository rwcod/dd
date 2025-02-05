"""Core functionality for text-to-image generation."""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

import torch
from diffusers import StableDiffusionPipeline
from pymongo import MongoClient
from pymongo.database import Database
import requests
from PIL import Image

from .config import Config
from .storage import StorageManager

logger = logging.getLogger(__name__)

@dataclass
class GenerationResult:
    """Result of a single image generation."""
    prompt_id: str
    prompt: str
    image_url: str

class ImageGenerator:
    """Handles text-to-image generation workflow."""

    def __init__(self, config: Config):
        """Initialize generator with configuration."""
        self.config = config
        
        # Initialize MongoDB
        self.mongo_client = MongoClient(config.mongo_uri)
        self.db: Database = self.mongo_client[config.database_name]
        logger.info(f"Connected to MongoDB: {config.database_name}")
        
        # Initialize storage
        self.storage = StorageManager(config)
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the Stable Diffusion model."""
        try:
            logger.info(f"Loading model: {self.config.model_id}")
            self.model = StableDiffusionPipeline.from_pretrained(
                self.config.model_id,
                torch_dtype=torch.float16 if self.config.device == "cuda" else torch.float32
            )
            self.model.to(self.config.device)
            logger.info(f"Model loaded successfully on {self.config.device}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    async def process_pending_prompts(self) -> List[GenerationResult]:
        """Process all pending prompts from MongoDB."""
        results = []
        
        try:
            # Find pending prompts
            pending = self.db[self.config.collection_name].find(
                {"status": "pending"}
            ).limit(self.config.batch_size)
            
            for prompt_doc in pending:
                try:
                    result = await self._process_single_prompt(prompt_doc)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error processing prompt {prompt_doc['_id']}: {str(e)}")
                    self._update_error_status(prompt_doc['_id'], str(e))
            
            if results and self.config.callback_url:
                await self._send_callback(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing prompts: {str(e)}")
            raise
    
    async def _process_single_prompt(self, prompt_doc: Dict) -> Optional[GenerationResult]:
        """Process a single prompt document."""
        try:
            prompt_id = str(prompt_doc['_id'])
            prompt_text = prompt_doc['text']
            
            logger.info(f"Processing prompt: {prompt_text[:50]}...")
            
            # Generate image
            image = await self._generate_image(prompt_text)
            
            # Upload to GCS
            filename = f"{prompt_id}_{int(datetime.now().timestamp())}.png"
            gcs_url = self.storage.upload_image(image, filename)
            
            # Update MongoDB
            self._update_success_status(prompt_id, gcs_url)
            
            return GenerationResult(
                prompt_id=prompt_id,
                prompt=prompt_text,
                image_url=gcs_url
            )
            
        except Exception as e:
            logger.error(f"Failed to process prompt {prompt_doc['_id']}: {str(e)}")
            self._update_error_status(prompt_doc['_id'], str(e))
            return None
    
    async def _generate_image(self, prompt: str) -> Image.Image:
        """Generate image from text prompt."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.model(
                prompt,
                num_inference_steps=self.config.num_inference_steps
            )["images"][0]
        )
    
    def _update_success_status(self, prompt_id: str, image_url: str) -> None:
        """Update document status after successful processing."""
        self.db[self.config.collection_name].update_one(
            {"_id": prompt_id},
            {
                "$set": {
                    "status": "completed",
                    "image_url": image_url,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"Updated status for prompt {prompt_id}: completed")
    
    def _update_error_status(self, prompt_id: str, error: str) -> None:
        """Update document status after processing error."""
        self.db[self.config.collection_name].update_one(
            {"_id": prompt_id},
            {
                "$set": {
                    "status": "error",
                    "error": error,
                    "error_at": datetime.utcnow()
                }
            }
        )
        logger.error(f"Updated status for prompt {prompt_id}: error")
    
    async def _send_callback(self, results: List[GenerationResult]) -> None:
        """Send callback with results if URL is configured."""
        if not self.config.callback_url:
            return
            
        try:
            data = {
                "results": [
                    {
                        "prompt_id": r.prompt_id,
                        "prompt": r.prompt,
                        "image_url": r.image_url
                    }
                    for r in results
                ]
            }
            
            response = requests.post(
                self.config.callback_url,
                json=data,
                timeout=self.config.callback_timeout
            )
            response.raise_for_status()
            logger.info(f"Callback sent successfully to {self.config.callback_url}")
            
        except Exception as e:
            logger.error(f"Callback failed: {str(e)}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.mongo_client.close()
            logger.info("Cleaned up resources")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()