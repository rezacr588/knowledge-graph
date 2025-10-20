"""
Structured logging configuration using loguru
"""

from loguru import logger
import sys
import json

def setup_logger(log_level: str = "INFO"):
    """
    Setup structured JSON logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Remove default handler
    logger.remove()
    
    # Add JSON structured logging
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level=log_level,
        colorize=True
    )
    
    # Add file logging
    logger.add(
        "logs/hybrid_rag_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    
    return logger

def log_request(request_id: str, endpoint: str, params: dict):
    """Log incoming request"""
    logger.info(f"Request: {request_id} | Endpoint: {endpoint} | Params: {json.dumps(params)}")

def log_response(request_id: str, status: int, duration_ms: float):
    """Log response"""
    logger.info(f"Response: {request_id} | Status: {status} | Duration: {duration_ms:.2f}ms")
