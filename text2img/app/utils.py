"""Utility functions and logging configuration."""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Configure logging with console and optional file output.
    
    Args:
        level: Logging level (INFO, DEBUG, etc.)
        log_file: Optional path to log file
        
    Returns:
        Configured logger instance
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level.upper())
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if requested
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def format_error(error: Exception) -> dict:
    """
    Format exception information for consistent error reporting.
    
    Args:
        error: Exception to format
        
    Returns:
        Dictionary with formatted error information
    """
    return {
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }

def validate_mongo_uri(uri: str) -> bool:
    """
    Validate MongoDB URI format.
    
    Args:
        uri: MongoDB connection URI to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Basic format validation
        if not uri.startswith(("mongodb://", "mongodb+srv://")):
            return False
        
        # Should contain host
        parts = uri.split("://")[1].split("/")
        if not parts[0]:  # No host
            return False
        
        return True
        
    except Exception:
        return False

def validate_gcs_bucket(bucket: str) -> bool:
    """
    Validate Google Cloud Storage bucket name format.
    
    Args:
        bucket: Bucket name to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # GCS bucket naming rules
        if not 3 <= len(bucket) <= 63:
            return False
        
        # Must start/end with letter/number
        if not (bucket[0].isalnum() and bucket[-1].isalnum()):
            return False
        
        # Can only contain lowercase letters, numbers, dots, and hyphens
        if not all(c.islower() or c.isdigit() or c in '.-' for c in bucket):
            return False
        
        return True
        
    except Exception:
        return False

class BatchProcessor:
    """Context manager for batch processing with progress tracking."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime.now()
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {self.description}: 0/{self.total}")
        return self
        
    def increment(self):
        """Increment progress counter and log progress."""
        self.current += 1
        logger = logging.getLogger(__name__)
        logger.info(f"{self.description} progress: {self.current}/{self.total}")
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        logger = logging.getLogger(__name__)
        logger.info(
            f"Completed {self.description}: {self.current}/{self.total} "
            f"in {duration.total_seconds():.2f}s"
        )