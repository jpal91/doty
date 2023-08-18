import logging

class CustomLogFormatter(logging.Formatter):
    bblue = '\033[1;34m'
    bwhite = '\033[1;37m'
    green = '\033[0;32m'
    byellow = '\033[1;33m'
    bred = '\033[1;31m'
    bmagenta = '\033[1;35m'
    bgreen = '\033[1;32m'
    end = '\033[0m'

    def __init__(self):
        super().__init__()
        self._fmt = self.set_fmt
        self._level = None
    
    @property
    def fmt(self) -> str:
        return self._fmt
    
    @fmt.setter
    def set_fmt(self, color: str = '\033[1;37m') -> None:
        self._fmt = f'{self.bblue}[{color}%(levelname)s{self.bblue}] [{self.green}%(asctime)s{self.bblue}] {self.byellow}%(module)s{self.end} %(message)s'
    
    @property
    def level(self) -> str:
        return self._level
    
    @level.setter
    def level(self, level: str) -> None:
        self._level = level
    
    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        
        if level == self.level:
            pass
        elif level == 'DEBUG':
            self.set_fmt = self.bmagenta
        elif level == 'INFO':
            self.set_fmt = self.bgreen
        elif level == 'WARNING':
            self.set_fmt = self.byellow
        
        self.level = level
        
        formatter = logging.Formatter(self.fmt)
        return formatter.format(record)