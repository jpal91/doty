import os
import yaml
from classes.logger import DotyLogger
from classes.entry import DotyEntry
from helpers.git import last_commit_file
from helpers.utils import write_lock_file

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

def get_new_entries(all_dotfiles: list[str], lock_entries: list[dict]) -> list[dict]:
    """Get all new entries to be added to the lock file"""
    current_names = [entry['name'] for entry in lock_entries]
    current_srcs = [entry['src'] for entry in lock_entries]
    current_dsts = [entry['dst'] for entry in lock_entries]

    new_entries = []

    for dotfile in all_dotfiles:
        name = os.path.basename(dotfile)
        src, dst = os.path.join(os.environ['HOME'], name), dotfile

        if any([name in current_names, src in current_srcs, dst in current_dsts]):
            continue
        
        entry = {
            'name': name,
            'src': src,
            'dst': dst,
            'linked': True,
            'link_name': name
        }
        new_entries.append(entry)
    return new_entries

def gen_temp_lock_file(entries: list[dict]) -> str:
    """Generate a temporary lock file"""
    temp_lock_file = os.path.join(os.environ['HOME'], 'dotfiles', '.doty_config', 'doty_lock_tmp.yml')
    write_lock_file(entries, temp_lock_file)
    return temp_lock_file

def discover() -> None:
    """Find any files in the dotfiles directory which are not linked yet"""
    logger.info('##bblue##Discovering new dotfiles in repo##end##')
    dotfiles = find_all_dotfiles()
    lock_entries = yaml.safe_load(last_commit_file(".doty_config/doty_lock.yml"))

    new_entries = get_new_entries(dotfiles, lock_entries)
    new_lock_entries = lock_entries + new_entries

    logger.info(f'##bgreen##Found {len(new_entries)} new dotfiles##end##')
    logger.info(f'##bblue##Writing new temp lock file##end##')
    temp_lock_file = gen_temp_lock_file(new_lock_entries)
    logger.info(f'##bgreen##Wrote temp lock file to {temp_lock_file}##end##')