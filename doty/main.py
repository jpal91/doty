
import os
from dotenv import load_dotenv
load_dotenv()

HOME=os.getenv("HOME")
DOTFILES=os.path.join(HOME, "dotfiles")