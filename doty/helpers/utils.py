import os
import shutil

def move_file(src, dst):
    """Move files from src to dst."""
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
            return os.path.exists(dst)