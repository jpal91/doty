import os
from update import update
from classes.DotyLogger import DotyLogger
from helpers.utils import move_file

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
    
    return user_input

def double_check(val: str, item_type: str) -> bool:
    """Helper function to ask user to double check their input and confirm it's correct when check is True"""
    try:
        user_input = input(f'\033[1;33mPlease confirm: \033[1;37m{item_type} = {val} (Y/n)\033[0m')
    except KeyboardInterrupt:
        logger.debug('KeyboardInterrupt')
        exit(0)
    
    if user_input == 'EXIT':
        logger.debug('User input was EXIT')
        exit(0)
    elif not user_input or user_input.lower() == 'y':
        return True
    else:
        return False

def get_name(check: bool = True) -> str:
    """Gets user input for entry 'name' of the dotfile they wish to add"""
    name = ''

    while not name:
        name = get_user_input('Enter the name of the dotfile: ')

        if not name:
            logger.warning('##bred##Name cannot be empty, please try again.')
        elif check and not double_check(name, 'Name'):
            name = ''
        else:
            break
    
    return name

def find_src(src: str) -> str:
    """Helps confirm src given by user is accurate and exists, returns empty string if not. 
    Assumes file is in the users home directory if no path is given"""
    home = os.environ['HOME']

    if not os.path.exists(src) and not src.startswith(home):
        src = os.path.join(home, src)
    
    if not os.path.exists(src):
        return ''
    
    return src

def get_src(check: bool = True) -> str:
    """Gets user input for the target dotfile's source path
    The function will continue until the user has input a correct path or they have exited.
    Will show warnings in the following situations -
        1. The user has a blank input
        2. The user has input a path that does not exist
        3. The user has input a path that is in the dotfiles directory
    """
    src = ''
    dotfiles_dir = os.environ['DOTFILES_PATH']

    while not src:
        user_input = get_user_input('Enter the source path of the dotfile: ')

        if not user_input:
            logger.warning('##bred##Source path cannot be empty, please try again.')
            continue

        src = find_src(user_input)

        if dotfiles_dir in src:
            logger.warning('##bred##Source path cannot be in dotfiles directory, please try again.')
            src = ''
            continue

        if not src:
            logger.warning('##bred##Source path does not exist, please try again.')
        elif check and not double_check(src, 'Source Path'):
            src = ''
        else:
            break

    return src

def check_dst(input: str) -> str:
    """Checks if the destination path exists, returns empty string if it does."""
    dotfiles_dir = os.environ['DOTFILES_PATH']
    dst = os.path.join(dotfiles_dir, input)
    
    if os.path.exists(dst):
        logger.warning('##bred##Destination path already exists, please try again.')
        return ''
    else:
        return dst

def get_dst(name: str, check: bool = True) -> str:
    """Gets user input for the target dotfile's destination path"""
    dst = ''
    dotfiles_dir = os.environ['DOTFILES_PATH']

    while not dst:
        user_input = get_user_input(f'##bwhite##Enter the destination path of the dotfile (or leave blank for default {name}):\n{dotfiles_dir}/')

        if not user_input:
            user_input = name

        dst = check_dst(user_input)

        if not dst:
            continue
        if check and not double_check(dst, 'Destination Path'):
            dst = ''
    
    return dst

def add_doty_ignore(name: str) -> None:
    """Helper function to add file to dotyignore if user indicated they do not want the file linked back to Home directory"""
    dotyignore_path = os.path.join(os.environ['DOTFILES_PATH'], '.doty_config', '.dotyignore')
    with open(dotyignore_path, 'a') as f:
        f.write(f'{name}\n')

def get_confirm_str(name: str, src: str, dst: str, linked: str) -> str:
    """Helper function to get the confirmation string sent to the user's console to confirm accuracy of entry"""
    return f'\n##bwhite##Name: {name}\n##bwhite##Source: {src}\n##bwhite##Destination: {dst}\n##bwhite##Linked: {linked}\n'

def add(entry_name: str = '', src: str = '', dst = '', no_git: bool = False, no_link: bool = False, force: bool = False) -> dict:
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
        logger.set_quiet()

    logger.info('##bwhite##Adding Dotfile\nType EXIT or press Ctrl+C to exit at any time.\n')

    # Gets entry name from user or uses the one provided
    if entry_name:
        name = entry_name
    else:
        name = get_name(check=not force)
    
    # Gets source path from user or uses the one provided
    if src:
        src_path = find_src(src)

        if not src_path:
            logger.error('##bred##Source path does not exist, aborting...')
            exit(1)
    else:
        src_path = get_src(check=not force)
    
    # Gets destination path from user or uses the one provided
    if dst:
        dst_path = check_dst(dst)

        if not dst_path:
            logger.error('##bred##Destination path already exists, aborting...')
            exit(1)
    else:
        dst_path = get_dst(name, check=not force)

    # First check to confirm the user wants to move source file to destination path
    if not force and not double_check(f'{src_path} -> {dst_path}', 'Create Doty Entry'):
        logger.warning('##byellow##Aborting...')
        exit(0)
    else:
        logger.info('##bgreen##Adding##end## ##bwhite##Dotfile Entry')
    
    # Checks if the user wants to link the file back to their home directory
    linked = not no_link

    # If user does not want to link back, the file is added to dotyignore so update will not link back
    if not linked:
        add_doty_ignore(os.path.basename(dst_path))
    
    # Second check that will show the full entry and ask user to confirm if the information is accurate
    # Skipped if force is True
    if force or (not force and double_check(get_confirm_str(name, src_path, dst_path, linked), 'Confirm Doty Entry')):
        logger.info('##bgreen##Adding##end## ##bwhite##Dotfile Entry')
    else:
        logger.warning('##byellow##Aborting...')
        exit(0)

    # Moves file from source path to destination path
    move_file(src_path, dst_path)

    # Updates git repo or not depending on no_git flag
    # Even if the user does not want to update the repo, update is still ran in case the user wants to link the file back
    if not no_git:
        logger.info('##bwhite##Adding to git repo')
        update(quiet=True)
    else:
        logger.info('##byellow##Skipping git repo update')
        update(commit=False, quiet=True)
    
    logger.info('##bgreen##Done')

    return {
        'name': name,
        'src': src_path,
        'dst': dst_path,
        'linked': linked,
    }


