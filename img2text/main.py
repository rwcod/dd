import argparse
import logging
import os
import sys

from app import Config, ImageCaptioner
from app.utils import setup_logging

def main():
    """Entry point for the Image-to-Text service."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Image to Text Caption Generator")
    parser.add_argument("--mongo_uri", help="MongoDB connection string")
    parser.add_argument("--dataset_id", help="Optional dataset ID to process")
    parser.add_argument("--callback_url", help="Optional callback URL")
    parser.add_argument("--log_level", default="INFO", help="Logging level")
    parser.add_argument("--log_file", help="Optional log file path")
    
    args = parser.parse_args()
    
    try:
        # Set up logging
        setup_logging(log_level=args.log_level, log_file=args.log_file)
        logger = logging.getLogger(__name__)
        
        # Set environment variables from arguments if provided
        if args.mongo_uri:
            os.environ['MONGO_URI'] = args.mongo_uri
        if args.dataset_id:
            os.environ['DATASET_ID'] = args.dataset_id
        if args.callback_url:
            os.environ['CALLBACK_URL'] = args.callback_url
        
        # Create configuration from environment
        config = Config.from_env()
        config.validate()
        
        # Process images
        with ImageCaptioner(config) as captioner:
            captioner.process_dataset()
            
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()