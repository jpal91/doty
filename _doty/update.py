import os
from helpers.discover import discover

def link_new_files(dotfiles: list) -> None:
    """Link new files in the repo"""
    for dotfile in dotfiles:
        base = os.path.basename(dotfile)
        home_path = os.path.join(os.environ['HOME'], base)
        os.symlink(dotfile, home_path)

def update():
    """Detect changes in the repo"""
    changes = discover()

    if changes:
        link_new_files(changes)