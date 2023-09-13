import os
import yaml
from classes.logger import DotyLogger
from classes.entry import DotyEntry
from helpers.git import last_commit_file, get_repo, checkout, make_commit
from helpers.utils import write_lock_file
from helpers.lock import compare_lock_yaml

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
    current_dsts = [entry['dst'] for entry in lock_entries]

    new_entries = []

    for dotfile in all_dotfiles:
        if dotfile in current_dsts:
            logger.debug(f'{dotfile} already in lock file. Skipping')
            continue

        name = os.path.basename(dotfile)

        if name in current_names:
            logger.warning(f'##bwhite##{name} ##byellow##already in lock file. Please add manually with a different name...')
            continue

        entry = DotyEntry({ 'name': name, 'dst': dotfile }).dict
        new_entries.append(entry)
        logger.debug(f'Adding entry {dotfile} to lock file')
    return new_entries

def gen_temp_lock_file(entries: list[dict]) -> str:
    """Generate a temporary lock file"""
    temp_lock_file = os.path.join(os.environ['HOME'], 'dotfiles', '.doty_config', 'doty_lock_tmp.yml')
    write_lock_file(entries, temp_lock_file)
    return temp_lock_file

def discover() -> None:
    """Find any files in the dotfiles directory which are not linked yet"""
    repo = get_repo()
    logger.info(f'##bwhite##Checking out branch ##byellow##"doty_discover"##bwhite## from ##byellow##{repo.head.shorthand}##end##')
    checkout(repo, 'doty_discover', override=True)

    logger.info('##bblue##Discovering new dotfiles in repo##end##')
    dotfiles = find_all_dotfiles()
    lock_entries = yaml.safe_load(last_commit_file(".doty_config/doty_lock.yml"))

    new_entries = get_new_entries(dotfiles, lock_entries)
    new_lock_entries = lock_entries + new_entries

    logger.info(f'##bgreen##Found {len(new_entries)} new dotfiles##end##')
    logger.info(f'##bblue##Writing new temp lock file##end##')
    lock_file_path = os.path.join(os.environ['DOTFILES_PATH'], '.doty_config', 'doty_lock.yml')
    write_lock_file(new_lock_entries, lock_file_path)
    make_commit(repo, 'Creating new lock file on discover')

    report = compare_lock_yaml(dry_run=True)
    report.gen_full_report(repo.status())

    logger.info(str(report))

