"""
Logging Configuration
Sets up structured logging for file and console output
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def setup_logging(log_level=logging.INFO):
    """
    Configure logging to both file and console
    
    Creates logs directory if it doesn't exist
    Logs to: logs/trading_bot.log
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger instance
    """
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Log file path
    log_file = log_dir / 'trading_bot.log'
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Prevent adding multiple handlers
    if logger.handlers:
        return logger
    
    # Format for logs
    log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # File handler - rotating log file (max 5MB per file, keep 5 files)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Log startup message
    logger.info("="*70)
    logger.info(f"Trading Bot Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_file.absolute()}")
    logger.info("="*70)
    
    return logger
