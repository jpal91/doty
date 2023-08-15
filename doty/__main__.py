import os
import shutil
from configparser import ConfigParser, ExtendedInterpolation
from classes import Doty

# HOME='/tmp/testdir'
# DOTFILES=os.path.join(HOME, "dotfiles")
# CONFIG=os.path.join(DOTFILES, ".dotyrc")
# dotycfg = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())

def create_symlink(src: str, dst: str):
    # if os.stat(src).st_size == 0:
    #     return
    
    if os.path.islink(dst):
        os.unlink(dst)
    os.symlink(src, dst)

def add_files(files: list, dir_name: str):
    
    for file in files:
        dot_path = os.path.join(dir_name, file)
        home_path = os.path.join(HOME, file)

        if not os.path.isfile(dot_path):
            
            if os.path.isfile(home_path):
                shutil.move(home_path, dot_path)
            else:
                with open(dot_path, "w") as f:
                    f.write("")
        
        create_symlink(dot_path, home_path)

# def main():
    
#     # TODO: Write some logic in case no config exists
#     dotycfg.read(CONFIG)
#     dir_files = [(fs[0], fs[1].strip().split('\n')) for fs in dotycfg.items('files')]
    
#     for df in dir_files:
#         name, files = df
#         dot_dir = os.path.join(DOTFILES, name)

#         if not os.path.isdir(dot_dir):
#             os.mkdir(dot_dir)
        
#         add_files(files, dot_dir)

def main():
    doty = Doty()
    doty.write_cfg()
    

if __name__ == "__main__":
    main()