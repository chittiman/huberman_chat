import logging
import sys

def setup_logging(level=logging.INFO, log_to_file=False, log_file='app.log'):
    """
    Set up logging for the application.

    Args:
        level: The minimum logging level to capture (e.g., logging.INFO, logging.DEBUG).
        log_to_file: If True, logs will be written to a file.
        log_file: The name of the file to log to.
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Clear existing handlers to avoid duplicate logs
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Create a handler for console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create a handler for file output if requested
    if log_to_file:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    logging.info("Logging configured successfully.")

if __name__ == '__main__':
    # Example usage:
    setup_logging(level=logging.DEBUG, log_to_file=True, log_file='debug.log')
    
    # Create a logger for this specific module to test
    logger = logging.getLogger(__name__)

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    print("\nCheck the console and 'debug.log' for output.")
