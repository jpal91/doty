import os
import logging
from typing import Any

class DotyLogger:

    def __init__(self, name: str = 'doty', file_logging: bool = True, level: int = logging.INFO) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)

        self.info_logger = logging.getLogger(f'{name}.info')
        self.info_logger.setLevel(logging.INFO)
    
    def get_logger(self) -> logging.Logger:
        return self.info_logger
    
    def get_debug_logger(self) -> logging.Logger:
        return self.logger

if __name__ == '__main__':
    dl = DotyLogger()
    logger = dl.get_debug_logger()
    logger.debug('test')