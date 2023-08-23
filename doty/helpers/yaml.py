import os
import yaml

DOTDIR = os.environ['DOTY_DIR']
CPATH = os.path.join(DOTDIR, '.doty_config')

def get_yaml(cfg: bool = True, lock: bool = True) -> tuple:

    if cfg:
        with open(os.path.join(CPATH, "dotycfg.yml")) as f:
            cfg_yml = yaml.safe_load(f)
    else:
        cfg_yml = None

    if lock:
        with open(os.path.join(CPATH, 'doty_lock.yml')) as f:
            lock_yml = yaml.safe_load(f)
    else:
        lock_yml = None

    return cfg_yml, lock_yml

def put_yaml(cfg_yml: list = None, lock_yml: list = None) -> None:
    if cfg_yml:
        with open(os.path.join(CPATH, "dotycfg.yml"), 'w') as f:
            yaml.safe_dump(cfg_yml, f, sort_keys=False)

    if lock_yml:
        with open(os.path.join(CPATH, "doty_lock.yml"), 'w') as f:
            f.write('# DO NOT TOUCH THIS FILE\n# This file is automatically generated by doty. Any changes made to this file will be overwritten\n\n')
            yaml.safe_dump(lock_yml, f, sort_keys=False)