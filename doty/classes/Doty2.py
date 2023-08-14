import os
import shutil
from collections import defaultdict
from configparser import ConfigParser, ExtendedInterpolation
from classes.DotyProfile import DotyProfile

# IDEA: Maybe use a class to represent the config file
# IDEA: Maybe use a class to represent each file - home path, dot path, link, etc.

HOME = '/tmp/dotytest' # os.environ['HOME']

class Doty:

    def __init__(self) -> None:
        self.dot_dir = os.path.join(HOME, "dotfiles")
        self.cfg_parser = self.load_cfg_parser()
        self.cfg = self.load_cfg()
    
    def load_cfg_parser(self) -> ConfigParser:
        # TODO: Write some logic in case no config exists
        if not os.path.isdir(self.dot_dir):
            print("Dotfiles directory does not exist")
            exit(1)
        
        cfg_parser = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
        cfg_parser.read(os.path.join(self.dot_dir, ".dotyrc"))
        return cfg_parser
    
    def load_cfg(self) -> dict:
        # cfg = defaultdict(list)
        cfg = []
        
        for section in self.cfg_parser.sections():
            if section == 'meta':
                continue
            
            if section == 'dotfiles':
                section_name = ''
            elif section.startswith('.'):
                print(f'Invalid section name {section} - section names cannot start with a period')
                continue
            # elif '.' in section:
            #     section_name = section.replace('.', '/')
            else:
                section_name = section
            
            dir_contents = self.cfg_parser.options(section)

            for d in dir_contents:
                target_path = os.path.join(self.dot_dir, section_name, d)
                current_path = os.path.join(HOME, d)

                cfg.append((target_path, current_path))
            
            
            # cfg[section_name] = self.cfg_parser.options(section)
        
        return cfg
    
    def check_valid(self):
        # for dir, files in self.cfg.items():
        #     dir_path = os.path.join(self.dot_dir, dir) if dir != '/' else self.dot_dir
        #     file_bases = [os.path.basename(file) for file in files]

        #     if not os.path.isdir(dir_path):
        #         os.makedirs(dir_path)

        #     # Checks that all file names in files are in dir_path
        #     for file in file_bases:
        #         file_path = os.path.join(dir_path, file)

        #         if not os.path.isfile(file_path):
        #             self.add_file(file_path)
            
        #     for file in os.listdir(dir_path):
        #         if file not in file_bases:
        #             self.add_to_cfg(dir, file)
        wanted_file_dirs = [fd for fd, _ in self.cfg]
        print(wanted_file_dirs)
        for i, fd in enumerate(wanted_file_dirs):
            if not os.path.exists(fd):
                self.add_target(i)
            
        for root, dirs, files in os.walk(self.dot_dir):
            for fp in [os.path.join(root, file) for file in files]:
                if '.dotyrc' in fp:
                    continue

                if fp not in wanted_file_dirs:
                    print(fp)
                    self.add_to_cfg(fp)
        
    def add_target(self, idx: int):
        target_path, home_path = self.cfg[idx]

        if not os.path.exists(home_path):
            print(f'Target {home_path} does not exist. Skipping...')
            return
        
        if not self.move_target(home_path, target_path):
            print(f'Error moving {home_path} to {target_path}. Skipping...')
            return
        
        print(f'Moved {home_path} to {target_path}')
        self.add_link(target_path, home_path)
    
    def move_target(self, src: str, dst: str) -> bool:
        attempted = False

        while True:
            try:
                shutil.move(src, dst)
            except FileNotFoundError:
                if attempted:
                    return False
                os.makedirs(os.path.dirname(dst))
                attempted = True
            else:
                return True
    
    def add_to_cfg(self, fp: str):
        file_parts = fp[1:].split('/')

        while file_parts[0] != 'dotfiles':
            file_parts.pop(0)
        
        if len(file_parts) <= 1:
            print(f'Error parsing {fp}. Skipping...')
            return
        elif len(file_parts) == 2:
            section = 'dotfiles'
            file = file_parts[1]
        else:
            section = '/'.join(file_parts[1:-1])
            file = file_parts[-1]
        
        if not self.cfg_parser.has_section(section):
            self.cfg_parser.add_section(section)
        self.cfg_parser.set(section, file, '')

        if not os.path.lexists(fp):
            self.add_link(fp, os.path.join(HOME, file))
    
    def add_link(self, src: str, dst: str):
        if os.path.islink(dst):
            os.unlink(dst)
        os.symlink(src, dst)
    
    def write_cfg(self):
        with open(os.path.join('/home/jpal/dev/doty', '.dotyrc-test'), 'w') as f:
            self.cfg_parser.write(f)
        
        link_parser = ConfigParser()
        link_parser.read_dict(
            { 'links': {
                src: dst for src, dst in self.cfg
            }}
        )

        with open(os.path.join('/home/jpal/dev/doty', '.doty_links'), 'w') as f:
            link_parser.write(f)
        