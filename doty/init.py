import os
import logging

logger = logging.getLogger('doty')

def create_dotyrc(dotyrc: str, home_path: str, dotfiles: str, logpath: str):
    logger.info('Creating Doty env file')
    os.makedirs(os.path.dirname(dotyrc), exist_ok=True)

    file_content = f"""\
    DOTHOME="{home_path}"
    DOTY_DIR="{dotfiles}"
    DOTY_LOG_PATH="{logpath}/doty.log"
    """

    with open(dotyrc, 'w') as f:
        f.write(file_content)

def create_dotfiles(dotfiles: str):
    logger.info('Creating Dotfiles directory')
    os.makedirs(dotfiles)

def create_doty_config_dir(doty_cfg_dir: str):
    logger.info('Creating Doty configuration directory')
    os.makedirs(doty_cfg_dir)

def create_doty_cfg(doty_cfg: str):
    logger.info('Creating Doty configuration file')
    with open(doty_cfg, 'w') as f:
        f.write('# Doty configuration file')

def create_doty_lock(doty_lock: str):
    logger.info('Creating Doty lock file')
    with open(doty_lock, 'w') as f:
        f.write('# Doty lock file')

def create_doty_logs(doty_logs: str):
    logger.info('Creating Doty logs directory')
    os.makedirs(doty_logs)

    with open(os.path.join(doty_logs, 'doty.log'), 'w') as f:
        f.write('# Doty logs file')

def main(alt_home: str = '', quiet: bool = False):
    if quiet:
        logger.setLevel(logging.ERROR)
    
    logger.info('Creating Doty - The Dotfiles Manager')
    
    home_path = os.environ['HOME'] if not alt_home else alt_home
    dotfiles = os.path.join(home_path, 'dotfiles')
    doty_cfg_dir = os.path.join(dotfiles, '.doty_config')
    dotyrc = os.path.join(doty_cfg_dir, 'dotyrc')
    doty_logs = os.path.join(dotfiles, 'logs')
    
    if not os.path.isdir(dotfiles):
        create_dotfiles(dotfiles)
    
    if not os.path.isdir(doty_cfg_dir):
        create_doty_config_dir(doty_cfg_dir)
    
    doty_cfg = os.path.join(doty_cfg_dir, 'dotycfg.yml')

    if not os.path.isfile(doty_cfg):
        create_doty_cfg(doty_cfg)
    
    doty_lock = os.path.join(doty_cfg_dir, 'doty_lock.yml')

    if not os.path.isfile(doty_lock):
        create_doty_lock(doty_lock)
    
    if not os.path.isdir(doty_logs):
        create_doty_logs(doty_logs)
    
    if not os.path.isfile(dotyrc):
        create_dotyrc(dotyrc, home_path, dotfiles, doty_logs)
    
    logger.info('Doty created successfully')