import os
import shutil

def attempt_move(src: str, dst: str) -> str:
    """Attempts to move the file from src to dst and returns the new dst"""
    attempted = False
    new_dst = ''

    while True:
        try:
            new_dst = shutil.move(src, dst)
        except FileNotFoundError:
            if attempted:
                return ''
            os.makedirs(os.path.dirname(dst))
            attempted = True
        else:
            return new_dst

def attempt_link(src: str, dst: str) -> bool:
    """Attempts to link the file from src to dst and returns True if successful, False otherwise"""
    if os.path.islink(src):
        os.unlink(src)
    
    try:
        os.symlink(dst, src)
    except FileNotFoundError:
        return False
    
    return True