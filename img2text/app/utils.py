import logging
import sys
from typing import Optional

def setup_logging(log_level: str = "INFO",
                 log_format: str = "%(asctime)s - %(levelname)s - %(message)s",
                 log_file: Optional[str] = None) -> None:
    """Configure logging for the application.
    
    Args:
        log_level: Logging level (default: INFO)
        log_format: Format string for log messages
        log_file: Optional file path for log output
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Basic configuration
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([] if log_file is None else [logging.FileHandler(log_file)])
        ]
    )
    
    # Set lower level for requests and urllib3
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def format_error(error: Exception) -> str:
    """Format an exception for error reporting.
    
    Args:
        error: The exception to format
        
    Returns:
        Formatted error message with type and details
    """
    return f"{type(error).__name__}: {str(error)}"