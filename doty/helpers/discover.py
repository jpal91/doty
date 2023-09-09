import os
import yaml
from classes.logger import DotyLogger
from helpers.utils import load_lock_file

logger = DotyLogger()

def find_all_dotfiles() -> list:
    """Find all dotfiles in the user's dotfile directory."""
    dot_dir = os.path.join(os.environ['HOME'], 'dotfiles')
    dotfiles = []

    for root, dirs, files in os.walk(dot_dir):
        # Skips .doty_config
        if '.doty_config' in dirs:
            dirs.remove('.doty_config')
        if '.git' in dirs:
            dirs.remove('.git')

        for file in files:
            if file == '.gitignore':
                continue
            dotfiles.append(os.path.join(root, file))
    return dotfiles

def _find_all_links(dotfiles: list) -> list:
    """Find all links in the user's home directory."""
    links = []
    for dotfile in dotfiles:
        base = os.path.basename(dotfile)
        home_path = os.path.join(os.environ['HOME'], base)
        if os.path.islink(home_path):
            links.append(home_path)
    return links

def _get_doty_ignore() -> list:
    """Get the contents of .dotyignore"""
    doty_ignore = os.path.join(os.environ['HOME'], 'dotfiles', '.doty_config', '.dotyignore')
    if os.path.isfile(doty_ignore):
        with open(doty_ignore, 'r') as f:
            items = [ item.strip() for item in f.readlines() if not item.startswith('#') ]
            return items
    return []

def _discover() -> list:
    """Find any files in the dotfiles directory which are not linked yet"""
    doty_ignore = _get_doty_ignore()
    dotfiles = find_all_dotfiles()
    links = _find_all_links(dotfiles)
    
    base_links = [os.path.basename(link) for link in links]
    new_link = [dotfile for dotfile in dotfiles if os.path.basename(dotfile) not in base_links and os.path.basename(dotfile) not in doty_ignore]
    unlink = [ignored for ignored in doty_ignore if ignored in base_links]

    return new_link, unlink



def discover() -> list:
    """Find any files in the dotfiles directory which are not linked yet"""
    doty_lock_path = os.path.join(os.environ['DOTFILES_PATH'], '.doty_config', 'doty_lock.yml')
    dotfiles = find_all_dotfiles()

    try:
        lock_entries = load_lock_file(doty_lock_path)
    except yaml.YAMLError as e:
        logger.critical('##bred##YAML file is invalid. Please check the file and try again.')
        exit(1)

    current_dsts = [entry['dst'] for entry in lock_entries]
    new_dotfiles = [df for df in dotfiles if df not in current_dsts]

    