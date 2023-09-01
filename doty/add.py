import os
from update import update
from classes.logger import DotyLogger
from classes.entry import DotyEntry
from helpers.utils import add_to_lock_file

logger = DotyLogger()

def get_user_input(prompt: str) -> str:
    """Helper function to get user input, catches keyboard interrupts or user input EXIT and exits"""
    try:
        user_input = input('\033[1;37m' + prompt + '\033[0m')
    except KeyboardInterrupt:
        logger.debug('KeyboardInterrupt')
        exit(0)
    
    if user_input == 'EXIT':
        logger.debug('User input was EXIT')
        exit(0)
    else:
        logger.debug(f'User input = {user_input}')
    
    return user_input

def double_check(val: str, item_type: str) -> bool:
    """Helper function to ask user to double check their input and confirm it's correct when check is True"""
    try:
        user_input = input(f'\033[1;33mPlease confirm: \033[1;37m{item_type} = {val} (Y/n)\033[0m ')
    except KeyboardInterrupt:
        logger.debug('KeyboardInterrupt')
        exit(0)
    
    if user_input == 'EXIT':
        logger.debug('User input was EXIT')
        exit(0)
    elif not user_input or user_input.lower() == 'y':
        logger.debug(f'User confirms check - {item_type} = {val}')
        return True
    else:
        logger.debug(f'User declines check - {item_type} = {val}')
        return False

def get_name() -> str:
    """Gets user input for entry 'name' of the dotfile they wish to add"""
    name = ''

    while not name:
        name = get_user_input('Enter the name of the dotfile: ')

        if not name:
            logger.warning('##bred##Name cannot be empty, please try again.')
    
    logger.debug(f'Entry name - {name}')
    return name

def get_src(name: str) -> str:
    """Gets user input for the target dotfile's source path
    The function will continue until the user has input a correct path or they have exited.
    Will show warnings in the following situations -
        1. The user has a blank input
        2. The user has input a path that does not exist
        3. The user has input a path that is in the dotfiles directory
    """
    src = ''
    home_path = os.environ['HOME']

    user_input = get_user_input(f'Enter the source path of the dotfile (or leave blank for {home_path}/{name}): ')

    if not user_input:
        src = os.path.join(home_path, name)
    else:
        src = os.path.realpath(os.path.expanduser(user_input))
        # src = os.path.realpath(user_input)
    
    logger.debug(f'Source path - {src}')
    return src

def get_dst(name: str) -> str:
    """Gets user input for the target dotfile's destination path"""
    dst = ''
    dotfiles_dir = os.environ['DOTFILES_PATH']

    user_input = get_user_input(f'Enter the destination path of the dotfile (or leave blank for default {dotfiles_dir}/{name}):\n{dotfiles_dir}/')

    if not user_input:
        dst = os.path.join(dotfiles_dir, name)
    else:
        dst = os.path.join(dotfiles_dir, user_input)

    logger.debug(f'Destination path - {dst}')
    return dst

def get_link_name(name: str) -> str:
    """Gets user input for the target dotfile's link name"""
    link_name = ''
    user_input = get_user_input(f'Enter the symlink name of the dotfile (or leave blank for default {name}): ')

    if not user_input:
        link_name = name
    else:
        link_name = user_input
    
    logger.debug(f'Link name - {link_name}')
    return link_name

def add(entry_name: str = '', src: str = '', dst: str = '', link_name: str = '', no_git: bool = False, no_link: bool = False, force: bool = False) -> dict:
    """Main function to add a new dotfile entry to the dotfiles repo. Takes user's command line inputs and queries for any missing info

    Args:
        entry_name (str, optional): Name of the dotfile entry. Defaults to ''.
        src (str, optional): Source path of the dotfile entry. Defaults to ''.
        dst ([type], optional): Destination path of the dotfile entry. Defaults to ''.
        no_git (bool, optional): Flag to skip updating the git repo. Defaults to False.
        no_link (bool, optional): Flag to skip linking the dotfile entry back to the user's home directory. Defaults to False.
        force (bool, optional): Flag to skip all user input and force the entry to be added. Defaults to False.
    
    Returns:
        dict: Dictionary containing the name, src, dst, and linked status of the entry added
    
    """
    # Force limits the amount of logging
    if force:
        logger.debug('Force flag set')
        logger.set_quiet()

    logger.info('\n##bblue##Adding Dotfile##end##\n##bwhite##Type EXIT or press Ctrl+C to exit at any time.\n')

    # Gets entry name from user or uses the one provided
    if entry_name:
        name = entry_name
    else:
        name = get_name()

    # Gets source path from user or uses the one provided
    if src:
        src_path = os.path.realpath(os.path.expanduser(src))
    else:
        src_path = get_src(name)

    # Gets destination path from user or uses the one provided
    if dst:
        dst_path = os.path.realpath(os.path.expanduser(dst))
    else:
        dst_path = get_dst(name)

    linked = not no_link

    if linked and not link_name:
        link_name = get_link_name(name)
    else:
        link_name = name

    # First check that cannot be skipped, asks user to confirm they are ok with moving a file that is not in their home directory
    # This prevents accidental moving of important system files to the dotfiles directory
    if not src_path.startswith(os.environ['HOME']) and not double_check('Source path is \033[1;31mnot in your home directory\033[0m, \033[1;37mare you sure you want to continue?', 'Source Path'):
        logger.warning('##byellow##Aborting...')
        exit(3)
    
    entry_dict = {
        'name': name,
        'src': src_path,
        'dst': dst_path,
        'link_name': link_name,
        'linked': linked
    }

    entry = DotyEntry(entry_dict)

    # Second check that will show the full entry and ask user to confirm if the information is accurate
    # Skipped if force is True
    if force or (not force and double_check('\n' + str(entry), 'Confirm Doty Entry')):
        logger.info('##bgreen##Adding##end## ##bwhite##Dotfile Entry')
    else:
        logger.warning('##byellow##Aborting...')
        exit(4)
    
    lock_path = os.path.join(os.environ['DOTFILES_PATH'], '.doty_config', 'doty_lock.yml')
    add_to_lock_file(entry_dict, lock_path)

    # Updates git repo or not depending on no_git flag
    # Even if the user does not want to update the repo, update is still ran in case the user wants to link the file back
    if not no_git and os.environ['GIT_AUTO_COMMIT']:
        logger.info('##bgreen##Adding##end## ##bwhite##to git repo')
        update()
    else:
        logger.info('##byellow##Skipping git repo update')
        update(commit=False, quiet=True)
    
    return entry_dict