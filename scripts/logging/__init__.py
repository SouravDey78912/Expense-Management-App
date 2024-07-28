import logging


def setup_logger(name, log_file, level=logging.DEBUG):
    """
    Function to set up a logger; creates handlers for both console and file output.

    Args:
        name (str): Name of the logger.
        log_file (str): File to log messages.
        level (int): Logging level (default is logging. DEBUG).

    Returns:
        logging.Logger: Configured logger.
    """

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file)

    # Set level for handlers
    c_handler.setLevel(level)
    f_handler.setLevel(level)

    # Create formatters and add them to handlers
    log_format = logging.Formatter(
        "%(asctime)s - %(levelname)-6s - [%(threadName)5s:%(funcName)5s("
        "): %(lineno)s] "
        "- %(message)s "
    )

    c_handler.setFormatter(log_format)
    f_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


logger = setup_logger("my_logger", "application.log")
