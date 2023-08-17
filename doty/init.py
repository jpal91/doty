import os

def create_dotyrc(dotyrc: str, home_path: str, dotfiles: str):
    print('Creating Doty env file')
    os.makedirs(os.path.dirname(dotyrc), exist_ok=True)

    file_content = f"""\
    DOTHOME="{home_path}"
    DOTY_DIR="{dotfiles}"
    """

    with open(dotyrc, 'w') as f:
        f.write(file_content)

def create_dotfiles(dotfiles: str):
    print('Creating Dotfiles directory')
    os.makedirs(dotfiles)

def create_doty_cfg(doty_cfg: str):
    print('Creating Doty configuration file')
    with open(doty_cfg, 'w') as f:
        f.write('# Doty configuration file')

def create_doty_lock(doty_lock: str):
    print('Creating Doty lock file')
    with open(doty_lock, 'w') as f:
        f.write('# Doty lock file')

def main(test: bool = False):
    print('Creating Doty - The Dotfiles Manager')
    
    home_path = os.environ['HOME'] if not test else '/tmp/dotytest'
    dotyrc = os.path.join(home_path, '.config', 'doty', 'dotyrc')
    dotfiles = os.path.join(home_path, 'dotfiles')

    if not os.path.isfile(dotyrc):
        create_dotyrc(dotyrc, home_path, dotfiles)
    
    if not os.path.isdir(dotfiles):
        create_dotfiles(dotfiles)
    
    doty_cfg = os.path.join(dotfiles, 'dotycfg.yml')

    if not os.path.isfile(doty_cfg):
        create_doty_cfg(doty_cfg)
    
    doty_lock = os.path.join(dotfiles, 'doty_lock.yml')

    if not os.path.isfile(doty_lock):
        create_doty_lock(doty_lock)
    
    print('Doty created successfully')