import os
from configparser import ConfigParser, ExtendedInterpolation

HOME = '/tmp/testdir' # os.environ['HOME']

class Doty:

    def __init__(self) -> None:
        self.dot_dir = os.path.join(HOME, "dotfiles")
        self.cfg = self.load_cfg()
        self.content = self.load_dir()
    
    def load_cfg(self) -> ConfigParser:
        # TODO: Write some logic in case no config exists
        if not os.path.isdir(self.dot_dir):
            print("Dotfiles directory does not exist")
            exit(1)
        
        cfg = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
        cfg.read(os.path.join(self.dot_dir, ".dotyrc"))
        return cfg
    
    def load_dir(self) -> list[tuple]:
        return [ (dir_or_file, content.strip().split('\n')) for dir_or_file, content in self.cfg.items('files') ]
        