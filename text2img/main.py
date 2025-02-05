#!/usr/bin/env python3
"""
Text-to-Image Generation Service
Processes text prompts from MongoDB, generates images using Stable Diffusion,
and stores them in Google Cloud Storage.
"""
import argparse
import asyncio
import sys
from pathlib import Path
from datetime import datetime

from app.config import Config
from app.core import ImageGenerator
from app.utils import setup_logging, validate_mongo_uri, validate_gcs_bucket

async def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Text-to-Image Generation Service",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--mongo-uri",
        required=True,
        help="MongoDB connection URI (e.g., mongodb://localhost:27017/dbname)"
    )
    
    parser.add_argument(
        "--gcs-bucket",
        required=True,
        help="Google Cloud Storage bucket name"
    )
    
    parser.add_argument(
        "--callback-url",
        help="Optional callback URL for completion notifications"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Optional log file path"
    )
    
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    args = parser.parse_args()

    try:
        # Validate arguments
        if not validate_mongo_uri(args.mongo_uri):
            parser.error("Invalid MongoDB URI format")
            
        if not validate_gcs_bucket(args.gcs_bucket):
            parser.error("Invalid GCS bucket name format")
        
        # Setup logging
        logger = setup_logging(
            level=args.log_level,
            log_file=args.log_file
        )
        
        logger.info("Starting Text-to-Image Generation Service")
        logger.info(f"MongoDB URI: {args.mongo_uri}")
        logger.info(f"GCS Bucket: {args.gcs_bucket}")
        
        if args.callback_url:
            logger.info(f"Callback URL: {args.callback_url}")
        
        # Initialize configuration
        config = Config.from_args(
            mongo_uri=args.mongo_uri,
            gcs_bucket=args.gcs_bucket,
            callback_url=args.callback_url
        )
        
        # Process images
        start_time = datetime.now()
        
        with ImageGenerator(config) as generator:
            results = await generator.process_pending_prompts()
            
            duration = datetime.now() - start_time
            logger.info(f"Processed {len(results)} images in {duration.total_seconds():.2f}s")
            
            for result in results:
                logger.info(f"Generated image: {result.image_url}")
                logger.info(f"Prompt: {result.prompt[:50]}...")
                logger.info("-" * 50)
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())