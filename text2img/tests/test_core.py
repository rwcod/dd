"""Unit tests for the text-to-image processor."""
import unittest
from unittest.mock import MagicMock, patch
import pytest
from pathlib import Path
import io

from PIL import Image
import torch

from app.config import Config
from app.core import ImageGenerator, GenerationResult
from app.storage import StorageManager

class TestConfig(unittest.TestCase):
    """Test configuration handling."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = Config(
            mongo_uri="mongodb://localhost:27017",
            database_name="test_db",
            gcs_bucket="test-bucket"
        )
        config.validate()  # Should not raise
        
        # Invalid config
        with self.assertRaises(ValueError):
            Config(
                mongo_uri="",
                database_name="test_db",
                gcs_bucket="test-bucket"
            ).validate()
            
        with self.assertRaises(ValueError):
            Config(
                mongo_uri="mongodb://localhost:27017",
                database_name="test_db",
                gcs_bucket="",
            ).validate()

class TestStorageManager(unittest.TestCase):
    """Test GCS storage operations."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = Config(
            mongo_uri="mongodb://localhost:27017",
            database_name="test_db",
            gcs_bucket="test-bucket"
        )
        
    @patch('google.cloud.storage.Client')
    def test_upload_image(self, mock_client):
        """Test image upload to GCS."""
        # Create test image
        image = Image.new('RGB', (100, 100), color='red')
        
        # Mock GCS
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Test upload
        storage = StorageManager(self.config)
        url = storage.upload_image(image, "test.png")
        
        self.assertTrue(url.startswith(f"gs://{self.config.gcs_bucket}/"))
        mock_blob.upload_from_file.assert_called_once()

class TestImageGenerator:
    """Test image generation and processing."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            mongo_uri="mongodb://localhost:27017",
            database_name="test_db",
            gcs_bucket="test-bucket"
        )
    
    @pytest.fixture
    def mock_mongo(self):
        """Create mock MongoDB client."""
        with patch('pymongo.MongoClient') as mock:
            yield mock
    
    @pytest.fixture
    def mock_storage(self):
        """Create mock StorageManager."""
        with patch('app.storage.StorageManager') as mock:
            yield mock
    
    @pytest.fixture
    def mock_model(self):
        """Create mock Stable Diffusion model."""
        with patch('diffusers.StableDiffusionPipeline.from_pretrained') as mock:
            yield mock
    
    @pytest.mark.asyncio
    async def test_process_pending_prompts(
        self,
        config,
        mock_mongo,
        mock_storage,
        mock_model
    ):
        """Test batch processing of prompts."""
        # Mock MongoDB data
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"_id": "1", "text": "test prompt 1", "status": "pending"},
            {"_id": "2", "text": "test prompt 2", "status": "pending"}
        ]
        mock_mongo.return_value.__getitem__.return_value = {
            config.collection_name: mock_collection
        }
        
        # Mock model output
        mock_image = Image.new('RGB', (64, 64), color='white')
        mock_model.return_value.return_value = {"images": [mock_image]}
        
        # Mock storage
        mock_storage.return_value.upload_image.return_value = "gs://test-bucket/test.png"
        
        # Process prompts
        generator = ImageGenerator(config)
        results = await generator.process_pending_prompts()
        
        # Verify results
        assert len(results) == 2
        assert all(isinstance(r, GenerationResult) for r in results)
        assert all("gs://" in r.image_url for r in results)
        
        # Verify MongoDB updates
        assert mock_collection.update_one.call_count == 2

if __name__ == '__main__':
    unittest.main()