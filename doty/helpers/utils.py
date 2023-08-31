import os
import shutil
import yaml

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

def load_lock_file(path: str) -> list:
    """Load the doty_lock.yml file."""
    with open(path, 'r') as f:
        lock_file = yaml.safe_load(f)
    return lock_file

def write_lock_file(entries: list[dict], path: str) -> None:
    """Write the doty_lock.yml file."""
    
    with open(path, 'w') as f:
        yaml.safe_dump(entries, f, sort_keys=False)