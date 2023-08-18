import os
import logging
import yaml
from classes import DotyEntry

HOME = os.environ['DOTHOME']
DOTDIR = os.environ['DOTY_DIR']
DPATH = os.environ['DPATH']

logger = logging.getLogger('doty')

def double_check(type: str, entry: str) -> bool:
    check = input(f"\033[1;33mPlease confirm {type} - \033[1;37m{entry}\033[0m \033[1;33m? (Y/n): \033[0m")

    if not check or check.lower() == 'y':
        return True
    return False

def check_dst(dst: str) -> str:
    path = os.path.join(DOTDIR, dst)
    if not os.path.exists(path):
        return path
    return ''

def find_file(name: str) -> str:
    if not os.path.isabs(name):
        path = os.path.join(HOME, name)
    else:
        path = name
    
    if os.path.exists(path):
        return path
    return ''

def get_input(prompt: str) -> str:
    try:
        inp = input('\033[0;36m' + prompt + '\033[0m')
    except KeyboardInterrupt:
        print('')
        exit(0)

    if inp == 'EXIT':
        exit(0)
    return inp

def main(check: bool, force: bool) -> None:
    if force:
        check = False
    
    with open(os.path.join(DOTDIR, "dotycfg.yml")) as f:
        cfg_yml = yaml.safe_load(f)

    with open(os.path.join(DOTDIR, 'doty_lock.yml')) as f:
        lock_yml = yaml.safe_load(f)
    
    if not cfg_yml and not lock_yml:
        logger.warning('dotycfg.yml is empty, please add entries to it')
        return
    
    logger.info('\n\033[1;33mCreating new Doty Entry...')
    logger.info('\033[1;37mTo quit at any time, enter EXIT or press Ctrl + C\n')
    current_names = { e['name'] for e in [*cfg_yml, *lock_yml] }
    name = ''
    
    while not name:
        name = get_input('Name of the file: ')
        
        if not name:
            logger.error('\033[1;31mName cannot be empty\n')
        elif name in current_names:
            logger.error('\033[1;31mFile name currently in configuration - please edit with doty update -e <NAME>')
            return
        elif check and not double_check('name', name):
            name = ''
        else:
            break

    logger.debug(f'Name - {name}')
    src = find_file(name)

    if src:
        check_src = get_input(f'Is this the file? - \033[1;37m{src}\033[0m \033[0;36m(Y/n): ')

        if check_src and check_src.lower() != 'y':
            src = ''
        
    while not src:
        # check_src = input('\033[1;33mPlease enter full file path, or path relative to your Home Directory: ')
        src_input = get_input('Please enter full file path, or path relative to your Home Directory: ')
        
        if not src_input:
            logger.error('\033[1;31mFile not found, please try again\n')
            continue
        
        src = find_file(src_input)

        if not src:
            logger.error('\033[1;31mFile not found, please try again\n')
        elif check and not double_check('source', src):
            src = ''
        else:
            break
    
    logger.debug(f'Src - {src}')
    dst = ''

    while not dst:
        dst_input = get_input(f'Please enter the new location in the Dotfiles directory (or press enter for {name}): \033[1;37m{DOTDIR}/\033[0m')

        if not dst_input:
            dst_input = name

        dst = check_dst(dst_input)

        if not dst:
            logger.error('\033[1;31mDestination already exists, please try again\n')
        elif check and not double_check('destination', dst):
            dst = ''
        else:
            break
    
    logger.debug(f'Dst - {dst}')
    notes = get_input('Please enter any notes for this entry (optional): ')
    linked = get_input('Should this entry be symlinked back to the Home Directory? (Y/n): ')

    if not linked or linked.lower() == 'y':
        linked = True
    else:
        linked = False
    
    logger.debug(f'Linked - {linked}')
    new_entry = DotyEntry({ 'name': name, 'src': src, 'dst': dst, 'notes': notes, 'linked': linked })

    if not force and not double_check('entry', new_entry):
        logger.info('\033[1;31mEntry creation cancelled\n')
        return

    new_entry.fix()

    if new_entry.entry_complete():
        lock_entry = new_entry.lock_entry()
    else:
        logger.error('\033[1;31mEntry is not valid, please try again\n')
    
    cfg_entry = new_entry.vals()

    with open(os.path.join(DPATH, "dotycfg.yml"), 'a') as f:
        yaml.safe_dump([cfg_entry], f, sort_keys=False)
    
    print('')
    logger.info('\033[1;36mAdded entry to dotycfg.yml')
    
    if not lock_entry:
        return
    
    with open(os.path.join(DPATH, "doty_lock.yml"), 'a') as f:
        yaml.safe_dump([lock_entry], f, sort_keys=False)
    
    logger.info('\033[1;36mAdded entry to doty_lock.yml')

    
