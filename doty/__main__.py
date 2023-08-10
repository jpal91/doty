import os
import shutil
from configparser import ConfigParser, ExtendedInterpolation

HOME='/tmp/testdir'
DOTFILES=os.path.join(HOME, "dotfiles")
CONFIG=os.path.join(DOTFILES, ".dotyrc")
dotycfg = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())

def add_files(files: list, dir_name: str):
    for file in files:
        path = os.path.join(dir_name, file)

        if not os.path.isfile(path):
            home_path = os.path.join(HOME, file)

            if os.path.isfile(home_path):
                shutil.move(home_path, path)
            else:
                with open(path, "w") as f:
                    f.write("")

def main():
    # TODO: Write some logic in case no config exists
    dotycfg.read(CONFIG)
    dir_files = [(fs[0], fs[1].strip().split('\n')) for fs in dotycfg.items('files')]
    
    for df in dir_files:
        name, files = df
        path = os.path.join(DOTFILES, name)

        if not os.path.isdir(path):
            os.mkdir(path)
        
        add_files(files, path)
    

if __name__ == "__main__":
    main()