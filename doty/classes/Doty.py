import os
import shutil
from configparser import ConfigParser, ExtendedInterpolation
from classes.DotyProfile import DotyProfile

HOME = '/tmp/dotytest' # os.environ['HOME']

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
        
    def add_dir(self, name: str, files: list) -> None:
        target_path = os.path.join(self.dot_dir, name)
        
        if os.path.isdir(target_path):
            return
        
        os.mkdir(target_path)

        for file in files:
            self.add_file(file, target_path)
        
        doty_profile = DotyProfile(target_path, name)

        with doty_profile as dp:
            dp.add_links(files)
    
    def add_file(self, name: str, dir: str = '') -> None:
        target_path = os.path.join(self.dot_dir, dir, name)
        home_path = os.path.join(HOME, name)
        
        if not os.path.isfile(target_path):
            if os.path.isfile(home_path):
                shutil.move(home_path, target_path)
            else:
                with open(target_path, "w") as f:
                    f.write("")
        
        self.add_link(target_path, home_path)
        
    def add_link(self, src: str, dst: str) -> None:
        if os.path.islink(dst):
            os.unlink(dst)
        os.symlink(src, dst)
    
    def update(self) -> None:
        for name, manifest in self.content:
            is_file = manifest is None or '.' in name

            if is_file:
                self.add_file(name)
            else:
                self.add_dir(name, manifest)