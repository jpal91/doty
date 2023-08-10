import os
from configparser import ConfigParser

HOME=os.getenv("HOME")
DOTFILES=os.path.join(HOME, "dotfiles")
CONFIG=os.path.join(DOTFILES, ".dotyrc")
dotycfg = ConfigParser(allow_no_value=True)

def main():
    # TODO: Write some logic in case no config exists
    dotycfg.read(CONFIG)
    sections = dotycfg.sections()
    print(dotycfg.items('dotyrc'))

if __name__ == "__main__":
    main()