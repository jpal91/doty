import os
import shutil
from update import update
from classes.DotyLogger import DotyLogger
from helpers.discover import find_all_dotfiles, find_all_links

logger = DotyLogger()

def remove_link(link: str) -> None:
    if os.path.islink(link):
        logger.info('##bred##Removing##end## ##bwhite##Home link')
        os.unlink(link)
    else:
        logger.error(f'\n##bred##Error##end## ##bwhite##Target {link} does not appear to be a link. Please remove manually')
        exit(1)

def remove_file(dotfile: str) -> None:
    home_path = os.path.join(os.environ['HOME'], os.path.basename(dotfile))
    
    if os.path.isfile(dotfile) and not os.path.isfile(home_path):
        logger.info('##bred##Removing##end## ##bwhite##Dotfile from dotfiles directory to HOME directory')
        shutil.move(dotfile, home_path)
    else:
        logger.error(f'\n##bred##Error##end## ##bwhite##Target {dotfile} does not appear to be a file. Please remove manually')
        exit(1)

def remove(name: str, link_only: bool = False, no_git: bool = False, force: bool = False) -> None:
    """Remove dotfiles from the repo"""
    dotfiles = find_all_dotfiles()
    links = find_all_links(dotfiles)
    matched_dotfile = [dotfile for dotfile in dotfiles if name in os.path.basename(dotfile)]
    matched_link = [link for link in links if name in os.path.basename(link)]

    if not matched_dotfile:
        logger.error(f'\n##byellow##Could not find dotfile {name}')
        exit(1)
    else:
        matched_dotfile = matched_dotfile[0]
    
    if not force:
        confirm = input(f'\n\033[1;33mAre you sure you want to remove {"link" if link_only else ""}\033[0m \033[1;37m{matched_dotfile}\033[1;33m? (y/N)\033[0m ')

        if confirm.lower() != 'y':
            logger.info('##byellow##Aborting')
            exit(0)
    
    if not matched_link:
        logger.warning(f'\n##byellow##Could not find link for dotfile {name}')
    else:
        remove_link(matched_link[0])
    
    if link_only:
        logger.info(f'\n##bgreen##Done##end## ##bwhite##Removed link for {matched_dotfile}')
        exit(0)
    
    remove_file(matched_dotfile)

    if not no_git and os.environ['GIT_AUTO_COMMIT']:
        update(quiet=True)
    else:
        update(commit=False, quiet=True)

    logger.info(f'\n##bgreen##Done##end##')
    

