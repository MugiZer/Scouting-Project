import logging
import traceback

# Configure logging once here
logging.basicConfig(
    level=logging.ERROR, 
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger("mountakhab")

def log_error(message):
    """Logs the error message and the full traceback."""
    logger.error("-" * 40)
    logger.error(f"ERROR: {message}")
    logger.error(traceback.format_exc())
    logger.error("-" * 40)
