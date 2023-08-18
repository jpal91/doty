import os
import logging
from classes import CustomLogFormatter

def init_file_logger() -> None:
    logger = logging.getLogger('doty')
    # logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(os.environ['DOTY_LOG_PATH'])
    fh.setLevel(logging.DEBUG)

    formatter = CustomLogFormatter()
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return