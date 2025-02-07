import unittest
from unittest.mock import Mock, patch
from PIL import Image

from app.config import Config
from app.core import ImageCaptioner

class TestImageCaptioner(unittest.TestCase):
    """Test cases for the ImageCaptioner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config(
            mongo_uri="mongodb://test:27017",
            model_name="test-model",
            use_gpu=False
        )
    
    @patch('app.core.BlipProcessor.from_pretrained')
    @patch('app.core.BlipForConditionalGeneration.from_pretrained')
    @patch('pymongo.MongoClient')
    def test_initialization(self, mock_mongo, mock_model, mock_processor):
        """Test ImageCaptioner initialization."""
        # Setup mocks
        mock_db = Mock()
        mock_mongo.return_value.get_default_database.return_value = mock_db
        
        # Create captioner
        captioner = ImageCaptioner(self.config)
        
        # Verify initialization
        self.assertEqual(captioner.config.mongo_uri, "mongodb://test:27017")
        mock_processor.assert_called_once_with("test-model")
        mock_model.assert_called_once_with("test-model")
        
    @patch('app.core.BlipProcessor.from_pretrained')
    @patch('app.core.BlipForConditionalGeneration.from_pretrained')
    @patch('pymongo.MongoClient')
    @patch('PIL.Image.open')
    def test_process_image(self, mock_image_open, mock_mongo, mock_model, mock_processor):
        """Test image processing."""
        # Setup mocks
        mock_db = Mock()
        mock_mongo.return_value.get_default_database.return_value = mock_db
        
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        mock_processor_instance.return_value = {"input_ids": Mock()}
        
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        mock_model_instance.generate.return_value = [Mock()]
        
        mock_processor_instance.decode.return_value = "A test caption"
        
        # Create captioner and process image
        captioner = ImageCaptioner(self.config)
        result = captioner.process_image("test_image.jpg")
        
        # Verify results
        self.assertEqual(result, "A test caption")
        mock_image_open.assert_called_once_with("test_image.jpg")
        
    @patch('app.core.BlipProcessor.from_pretrained')
    @patch('app.core.BlipForConditionalGeneration.from_pretrained')
    @patch('pymongo.MongoClient')
    def test_process_dataset(self, mock_mongo, mock_model, mock_processor):
        """Test dataset processing."""
        # Setup mocks
        mock_db = Mock()
        mock_mongo.return_value.get_default_database.return_value = mock_db
        
        mock_images = [
            {"_id": "1", "path": "image1.jpg"},
            {"_id": "2", "path": "image2.jpg"}
        ]
        mock_db.images.find.return_value = mock_images
        
        # Create captioner with mocked process_image
        captioner = ImageCaptioner(self.config)
        captioner.process_image = Mock(return_value="Test caption")
        
        # Process dataset
        captioner.process_dataset()
        
        # Verify processing
        self.assertEqual(captioner.process_image.call_count, 2)
        self.assertEqual(
            mock_db.images.update_one.call_count,
            2,
            "Should update status for both images"
        )

if __name__ == '__main__':
    unittest.main()