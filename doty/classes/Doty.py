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

    def move_file(self, src: str, dst: str) -> bool:
        attempted = False

        while True:
            try:
                shutil.move(src, dst)
            except FileNotFoundError:
                os.makedirs(os.path.dirname(dst))
            else:
                break
            finally:
                if attempted:
                    print(f"Could not move {src} to {dst}")
                    return False
                attempted = True
        
        return True
    
    def mkdotdir(self, name: str, root_dir: str, files: list) -> None:
        os.mkdir(root_dir)

        doty_profile = DotyProfile(root_dir, name)

        with doty_profile as dp:
            dp.add_links(files)

    def add_existing_dir(self, dir_path: str, files: list) -> None:
        name = os.path.basename(dir_path)
        dot_dir_path = os.path.join(self.dot_dir, name)

        print(f'Moving existing directory {dir_path} to {dot_dir_path}')

        if not os.path.isdir(dot_dir_path):
            self.mkdotdir(name, dot_dir_path, files)
            print(f'Creating new directory {dot_dir_path} and moving files...')
        
        for file in files:
            full_path = os.path.join(dir_path, file)

            if os.path.isfile(full_path):
                new_path = os.path.join(dot_dir_path, file)
                move_success = self.move_file(full_path, new_path)

                if not move_success:
                    print(f"Could not move {full_path} to {new_path}")
                    continue

                self.add_link(new_path, full_path)
        
        
        
    def add_dir(self, name: str, files: list) -> None:
        target_path = os.path.join(self.dot_dir, name)
        
        if not os.path.isdir(target_path):
            self.mkdotdir(name, target_path, files)
            print(f'Creating new directory {target_path} and moving files...')
        else:
            print(f'Directory {target_path} already exists. Moving files...')
        
        # home_path = os.path.join(HOME, name)

        # if os.path.isdir(home_path):
        #     self.add_existing_dir(home_path, files)
        # else:
        #     os.mkdir(target_path)

        for file in files:
            self.add_file(file, target_path)
        
        # doty_profile = DotyProfile(target_path, name)

        # with doty_profile as dp:
        #     dp.add_links(files)
    
    def add_file(self, name: str, dir: str = '') -> None:
        target_path = os.path.join(self.dot_dir, dir, name)
        home_path = os.path.join(HOME, name)
        
        if not os.path.isfile(target_path) and os.path.isfile(home_path):
            # shutil.move(home_path, target_path)
            move_success = self.move_file(home_path, target_path)

            if not move_success:
                print(f"Could not move {home_path} to {target_path}")
                return
        else:
            print(f'Cannot find file: {name}. Skipping...')
            return
        
        self.add_link(target_path, home_path)
        print(f'Added {name} to {dir if dir else "dotfiles"}')
        
    def add_link(self, src: str, dst: str) -> None:
        if os.path.islink(dst):
            os.unlink(dst)
        os.symlink(src, dst)
    
    def update(self) -> None:
        for name, manifest in self.content:
            # is_file = manifest is None or '.' in name

            # if is_file:
            #     self.add_file(name)
            # else:
            #     self.add_dir(name, manifest)
            home_path = os.path.join(HOME, name)

            if os.path.isfile(home_path):
                self.add_file(name)
            elif os.path.isdir(home_path):
                self.add_existing_dir(home_path, manifest)
            elif manifest:
                self.add_dir(name, manifest)
            else:
                print(f'Cannot find file or directory: {name}. Skipping...')
                continue