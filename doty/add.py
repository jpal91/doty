import os
from update import update
# from classes.DotyLogger import DotyLogger
from helpers.logger import init_dotylogger
from helpers.utils import move_file

# logger = DotyLogger()
logger = init_dotylogger()

# DOTFILES_PATH = os.environ['DOTFILES_PATH']

def get_user_input(prompt: str) -> str:
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
    home = os.environ['HOME']

    if not src.startswith(home):
        src = os.path.join(home, src)
    
    if not os.path.exists(src):
        return ''
    
    return src

def get_src(check: bool = True) -> str:
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
    dotfiles_dir = os.environ['DOTFILES_PATH']
    dst = os.path.join(dotfiles_dir, input)
    
    if os.path.exists(dst):
        logger.warning('##bred##Destination path already exists, please try again.')
        return ''
    else:
        return dst

def get_dst(name: str, check: bool = True) -> str:
    dst = ''
    dotfiles_dir = os.environ['DOTFILES_PATH']

    while not dst:
        # logger.info(f'##bwhite##Enter the destination path of the dotfile (or leave blank for default {name}):')
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
    dotyignore_path = os.path.join(os.environ['DOTFILES_PATH'], '.doty_config', '.dotyignore')
    with open(dotyignore_path, 'a') as f:
        f.write(f'{name}\n')

def add(entry_name: str = '', src: str = '', dst = '', no_git: bool = False, no_link: bool = False, force: bool = False) -> None:
    if force:
        logger.set_quiet()
    logger.info('##bwhite##Adding Dotfile\nType EXIT or press Ctrl+C to exit at any time.\n')

    if entry_name:
        name = entry_name
    else:
        name = get_name(check=not force)
    
    if src:
        src_path = find_src(src)

        if not src_path:
            logger.error('##bred##Source path does not exist, aborting...')
            exit(1)
    else:
        src_path = get_src(check=not force)
    
    if dst:
        dst_path = check_dst(dst)

        if not dst_path:
            logger.error('##bred##Destination path already exists, aborting...')
            exit(1)
    else:
        dst_path = get_dst(name, check=not force)

    if not force and not double_check(f'{src_path} -> {dst_path}', 'Create Doty Entry'):
        logger.warning('##byellow##Aborting...')
        exit(0)
    else:
        logger.info('##bgreen##Adding##end## ##bwhite##Dotfile Entry')
    
    move_file(src_path, dst_path)
    
    linked = not no_link

    if not linked:
        add_doty_ignore(os.path.basename(dst_path))

    if not no_git:
        logger.info('##bwhite##Adding to git repo')
        update

if __name__ == '__main__':
    get_name()