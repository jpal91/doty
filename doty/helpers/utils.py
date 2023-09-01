import os
import shutil
import yaml

class DesinationExistsError(Exception):
    """Raised when the destination path already exists."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

def move_file(src, dst):
    """Move files from src to dst."""
    attempted = False

    if os.path.exists(dst):
        raise DesinationExistsError(f'{dst} already exists.')

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

def move_out(dst, src):
    """Move files out of dotfiles directory"""

    if os.path.exists(src):
        raise DesinationExistsError(f'{src} already exists.')

    # Move file
    shutil.move(dst, src)

    # Remove any empty directories left behind
    dir_path = os.path.dirname(dst)
    try:
        os.removedirs(dir_path)
    except OSError:
        pass

def load_lock_file(path: str) -> list:
    """Load the doty_lock.yml file."""
    with open(path, 'r') as f:
        lock_file = yaml.safe_load(f)
    return lock_file or []

def write_lock_file(entries: list[dict], path: str) -> None:
    """Write the doty_lock.yml file."""
    
    with open(path, 'w') as f:
        f.write('# Path: ~/.doty_config/doty_lock.yml\n')
        f.write('# This file is used to keep track of dotfiles and their respective repositories.\n')
        f.write('# It is recommended that you do not edit this file directly.\n')
        f.write('# Instead, use the \'doty add\' command.\n')
        if entries:
            yaml.safe_dump(entries, f, sort_keys=False)

def add_to_lock_file(entry: dict, path: str) -> bool:
    """Adds an entry to the doty_lock.yml file."""
    lock_file = load_lock_file(path)
    entry_names = [e['name'] for e in lock_file]

    if entry_names and entry['name'] in entry_names:
        return False
    
    lock_file.append(entry)
    write_lock_file(lock_file, path)
    return True