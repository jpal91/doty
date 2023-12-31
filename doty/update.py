import os
from classes.logger import DotyLogger
from helpers.discover import discover
from helpers.git import make_commit, get_repo, parse_status
from helpers.lock import compare_lock_yaml

logger = DotyLogger()

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
    message = f'Links(A{links}|R{unlinks})' + parse_status(repo)
    logger.debug(f'Committing changes: {message}')
    make_commit(repo, message)

def _update(commit: bool = os.getenv('GIT_AUTO_COMMIT', True), quiet: bool = False, dry_run: bool = False):
    """Detect changes in the repo"""

    if dry_run:
        quiet = False

    if quiet:
        logger.set_quiet()

    logger.info('\n##bblue##Discovering changes and updating Dotfiles Repo\n')
    links, unlinks = discover()

    if dry_run:
        logger.info('##yellow##Dry run, no changes will be made')
        logger.info(f'##bgreen##Linking##end## ##bwhite##{len(links)} new files')
        logger.info(f'##bred##Unlinking##end## ##bwhite##{len(unlinks)} files')
        return

    if links:
        logger.info(f'##bgreen##Linking##end## ##bwhite##{len(links)} new files')
        link_new_files(links)
    
    if unlinks:
        logger.info(f'##bred##Unlinking##end## ##bwhite##{len(unlinks)} files')
        unlink_files(unlinks)
    
    if not links and not unlinks:
        logger.info('##byellow##No changes detected')
        return
    
    if commit:
        logger.info('##bwhite##Committing changes')
        commit_changes(len(links), len(unlinks))

    # Resetting in case quiet was called from another function
    if quiet:
        logger.set_info()

def update(commit: bool = os.getenv('GIT_AUTO_COMMIT', True), quiet: bool = False, dry_run: bool = False):
    """Detect changes in the repo"""

    if dry_run:
        quiet = False
        logger.info('\n##byellow##!!Dry run, no changes will be made!!')
    
    if quiet:
        logger.set_quiet()
    else:
        logger.set_info()

    logger.info('\n##bblue##Discovering changes and updating Dotfiles Repo\n')

    report = compare_lock_yaml(dry_run=dry_run)
    repo = get_repo()
    report.gen_full_report(repo.status())

    logger.info(str(report))

    if not dry_run and commit and report.changes:
        logger.info('##bwhite##Committing changes')
        make_commit(repo, report.git_report)
    else:
        logger.info('##byellow##Skipping git repo update')