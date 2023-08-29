import os
import re
import logging

class DotyFilter(logging.Filter):
    bblue = '\033[1;34m'
    bwhite = '\033[1;37m'
    green = '\033[0;32m'
    yellow = '\033[0;33m'
    byellow = '\033[1;33m'
    bred = '\033[1;31m'
    bmagenta = '\033[1;35m'
    bgreen = '\033[1;32m'
    end = '\033[0m'

    def __init__(self, color: bool = True):
        super().__init__()
        self.color = color

    def filter_color(self, msg: str) -> str:
        match = re.findall(r'##([a-z]+)##', msg)

        if not match:
            return msg
        
        for color in match:
            if self.color:
                msg = msg.replace(f'##{color}##', self.__getattribute__(color))
            else:
                msg = msg.replace(f'##{color}##', '')

        return msg + self.end
    
    def filter(self, record) -> bool:
        # print(record)
        record.msg = self.filter_color(record.msg)
        return True

class CustomFileLogFormatter(logging.Formatter):
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

class DotyLogger:
    bblue = '\033[1;34m'
    bwhite = '\033[1;37m'
    green = '\033[0;32m'
    yellow = '\033[0;33m'
    byellow = '\033[1;33m'
    bred = '\033[1;31m'
    bmagenta = '\033[1;35m'
    bgreen = '\033[1;32m'
    end = '\033[0m'

    def __init__(self, name: str = 'doty', file_logging: bool = True, color: bool = os.getenv('DOTY_COLOR_LOGGING', True)) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)

        self.color = color

        self.filter = DotyFilter(self.color)

        self.logger.addFilter(self.filter)

        if file_logging:
            self.file_handler = logging.FileHandler(os.path.join(os.environ['HOME'], 'dotfiles', '.doty_config', 'doty.log'))
            self.file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(self.file_handler)

            if color:
                self.file_handler.setFormatter(CustomFileLogFormatter())
            else:
                self.file_handler.setFormatter(logging.Formatter('%(levelname)s [%(asctime)s] %(module)s %(message)s'))
    
    def set_color(self, color: bool) -> None:
        self.color = color

    def set_debug(self) -> None:
        self.handler.setLevel(logging.DEBUG)
    
    def set_info(self) -> None:
        self.handler.setLevel(logging.INFO)
    
    def set_quiet(self) -> None:
        self.handler.setLevel(logging.WARNING)
    
    def filter_color(self, msg: str) -> str:
        match = re.findall(r'##([a-z]+)##', msg)

        if not match:
            return msg
        
        for color in match:
            if self.color:
                msg = msg.replace(f'##{color}##', self.__getattribute__(color))
            else:
                msg = msg.replace(f'##{color}##', '')

        return msg + self.end
    
    def debug(self, msg, *args, **kwargs) -> None:
        msg = self.filter_color(msg)
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs) -> None:
        msg = self.filter_color(msg)
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs) -> None:
        msg = self.filter_color(msg)
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs) -> None:
        msg = self.filter_color(msg)
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs) -> None:
        msg = self.filter_color(msg)
        self.logger.critical(msg, *args, **kwargs)


if __name__ == '__main__':
    logger = DotyLogger(color=False)
    # logger.info('Normal logger - test')
    # logger.debug('Normal logger - test')
    # logger.info('##bblue##Custom logger - test##end##')
    # logger.set_debug()
    # logger.info('Debug logger - test')
    # logger.debug('Debug logger - test')
    logger.warning('Test Warning')
    # logger = logging.getLogger('doty')
    # logger.info('Test1')
    # dl = DotyLogger()
    # logger = logging.getLogger('doty')
    # logger.info('Test2')
    
