import logging

def setup_logging(log_level, log_file):
    logging.basicConfig(level=log_level, filename=log_file)
    return logging.getLogger(__name__)