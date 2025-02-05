"""Google Cloud Storage operations for image storage."""
import io
from typing import Optional
from pathlib import Path
import logging

from google.cloud import storage
from google.cloud.storage import Blob, Bucket
from PIL import Image

from .config import Config

logger = logging.getLogger(__name__)

class StorageManager:
    """Handles Google Cloud Storage operations."""
    
    def __init__(self, config: Config):
        """Initialize GCS client and bucket."""
        self.config = config
        self.client = storage.Client()
        self.bucket = self.client.bucket(config.gcs_bucket)
        logger.info(f"Initialized GCS connection to bucket: {config.gcs_bucket}")
    
    def upload_image(self, image: Image.Image, filename: str) -> str:
        """
        Upload an image to GCS and return its URL.
        
        Args:
            image: PIL Image to upload
            filename: Desired filename in GCS
        
        Returns:
            GCS URL for the uploaded image
        """
        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Construct blob path
            blob_path = f"{self.config.gcs_prefix}/{filename}"
            blob: Blob = self.bucket.blob(blob_path)
            
            # Upload with content type
            blob.upload_from_file(
                img_byte_arr,
                content_type='image/png',
                timeout=30
            )
            
            url = f"gs://{self.config.gcs_bucket}/{blob_path}"
            logger.info(f"Uploaded image to: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload image {filename}: {str(e)}")
            raise
    
    def delete_image(self, url: str) -> None:
        """
        Delete an image from GCS.
        
        Args:
            url: GCS URL of the image to delete
        """
        try:
            # Extract blob path from URL
            path = url.replace(f"gs://{self.config.gcs_bucket}/", "")
            blob: Blob = self.bucket.blob(path)
            
            # Delete if exists
            if blob.exists():
                blob.delete()
                logger.info(f"Deleted image: {url}")
            else:
                logger.warning(f"Image not found: {url}")
                
        except Exception as e:
            logger.error(f"Failed to delete image {url}: {str(e)}")
            raise
    
    def get_image_data(self, url: str) -> Optional[bytes]:
        """
        Retrieve image data from GCS.
        
        Args:
            url: GCS URL of the image
            
        Returns:
            Image data as bytes, or None if not found
        """
        try:
            # Extract blob path from URL
            path = url.replace(f"gs://{self.config.gcs_bucket}/", "")
            blob: Blob = self.bucket.blob(path)
            
            # Download if exists
            if blob.exists():
                return blob.download_as_bytes()
            else:
                logger.warning(f"Image not found: {url}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve image {url}: {str(e)}")
            raise