import os
import yaml
from pygit2 import Repository
from helpers.git import get_status

def at_dst(lock: dict) -> bool:
    pass

def at_src(lock: dict) -> bool:
    pass

def check_duplicates(lock_yml: list[dict]) -> bool:
    """Checks for duplicate entries in the lock file and returns True if duplicates are found, False otherwise"""
    names = [ e['name'] for e in lock_yml if 'name' in e ] 

    if len(names) != len(set(names)):
        return True
    
    return False

def autocomplete_entries(lock_yml: list[dict]) -> list[dict]:
    """Autocompletes entries in the lock file and returns the updated lock file"""
    pass

def lock_file_changes(lock_yml: list[dict]) -> bool:
    """Checks validity of lock file and returns True if changes are valid, False otherwise"""
    
    if check_duplicates():
        return False
    
    for lock in lock_yml:
        if not at_src(lock) or not at_dst(lock):
            return False

def update():
    """Detect changes in the repo"""
    dotfiles = os.path.join(os.environ['HOME'], 'dotfiles')
    repo = Repository(os.path.join(dotfiles, '.git'))
    changes = get_status(repo)

    if changes and 'doty_lock.yml' in changes:
        with open(os.path.join(dotfiles, '.doty_config', 'doty_lock.yml'), 'r') as doty_lock:
            doty_lock = yaml.safe_load(doty_lock)

        lock_changes = lock_file_changes(doty_lock)