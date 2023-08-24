import os
import logging
from helpers.discover import discover
from helpers.git import make_commit, get_repo

logger = logging.getLogger('doty')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

logger.han

def link_new_files(dotfiles: list) -> None:
    """Link new files in the repo"""
    for dotfile in dotfiles:
        base = os.path.basename(dotfile)
        home_path = os.path.join(os.environ['HOME'], base)
        logger.debug(f'Linking {dotfile} to {home_path}')
        os.symlink(dotfile, home_path)

def unlink_files(dotfiles: list) -> None:
    """Unlink files in the repo"""
    for dotfile in dotfiles:
        home_path = os.path.join(os.environ['HOME'], dotfile)
        logger.debug(f'Unlinking {home_path}')
        os.unlink(home_path)

def commit_changes(links: int, unlinks: int) -> None:
    """Commit changes to the repo"""
    repo = get_repo()
    repo_status = repo.status()
    file_changes = ' | File Changes' if repo_status else ''
    message = f'Links(A{links}|R{unlinks}){file_changes}'
    logger.debug(f'Committing changes: {message} - {repo_status}')
    make_commit(repo, message)

def update(commit: bool = True):
    """Detect changes in the repo"""
    logger.info('Discovering changes and updating Dotfiles Repo')
    links, unlinks = discover()

    if links:
        link_new_files(links)
    
    if unlinks:
        unlink_files(unlinks)
    
    if commit:
        commit_changes(len(links), len(unlinks))
    