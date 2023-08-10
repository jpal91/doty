import os
from configparser import ConfigParser, ExtendedInterpolation

HOME=os.getenv("HOME")
DOTFILES=os.path.join(HOME, "dotfiles")
CONFIG=os.path.join(DOTFILES, ".dotyrc")
dotycfg = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())

def main():
    # TODO: Write some logic in case no config exists
    dotycfg.read(CONFIG)
    sections = dotycfg.sections()
    print(dotycfg['manifest']['multiline'])
    

if __name__ == "__main__":
    main()