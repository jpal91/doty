import os
import logging
import yaml
from classes import DotyEntries

HOME = os.environ['DOTHOME']
DOTDIR = os.environ['DOTY_DIR']
DPATH = os.environ['DPATH']

logger = logging.getLogger('doty')

def compare_lock(cfg_entries: DotyEntries, lock_entries: DotyEntries) -> tuple:
    logger.info('\nRunning initial checks and detecting changes...\n')

    add, remove, update, no_change = [], [], [], 0
    entry_dict = { e.name: e for e in cfg_entries.entries if not e.is_broken_entry() }

    for le in lock_entries.entries:
        name = le.name
        cfg_entry = entry_dict.get(name, None)

        if cfg_entry is None:
            remove.append(le)
        elif cfg_entry != le:
            update.append((le, cfg_entry))
            del entry_dict[name]
        else:
            le.notes = cfg_entry.notes
            del entry_dict[name]
            no_change += 1
    
    remainder = entry_dict.values()
    add.extend(remainder)
    insert, delete, upd = len(remainder), len(remove), len(update)

    logger.info(f'Adding {insert} entries\nRemoving {delete} entries\nUpdating {upd} entries\nNo change to {no_change} entries\n')

    return add, remove, update

def delete_ent(locks: list, cfgs: list) -> list:
    options = [ f'{i+1}. {c["name"]}' for i, c in enumerate(locks)]
    str_options = "\n" + "\n".join(options)

    while True:
        try:
            user_input = input(f'\n\033[1;36mWhich entry would you like to delete? \033[1;37m{str_options}\n\033[0;36m\n(Enter number or EXIT to cancel): \033[0m')
        except KeyboardInterrupt:
            print('')
            exit(0)

        if user_input == 'EXIT':
            exit(0)
        elif not user_input.isnumeric():
            logger.error('\n\033[1;33mInvalid input, please enter a number')
            continue
        elif int(user_input) < 1 or int(user_input) > len(locks):
            logger.error('\n\033[1;33mInvalid input, please enter a valid option')
            continue
        else:
            break
    
    target = locks[int(user_input) - 1]['name']
    idx = [ i for i, c in enumerate(cfgs) if c['name'] == target ][0]
    
    try:
        confirm = input(f'\n\033[1;31mAre you sure you want to delete \033[1;37m{target}\033[1;31m ? (y/N): \033[0m')
    except KeyboardInterrupt:
        print('')
        exit(0)
    
    if confirm and confirm.lower() == 'y':
        del cfgs[idx]
    else:
        logger.info('\033[1;36mAborting...')
        exit(0)

    return cfgs

def main(delete: bool = False):

    with open(os.path.join(DOTDIR, "dotycfg.yml")) as f:
        cfg_yml = yaml.safe_load(f)

    with open(os.path.join(DOTDIR, 'doty_lock.yml')) as f:
        lock_yml = yaml.safe_load(f)
    
    if not cfg_yml and not lock_yml:
        logger.warning('dotycfg.yml is empty, please add entries to it')
        return
    
    if delete:
        cfg_yml = delete_ent(lock_yml, cfg_yml)
    
    cfg = DotyEntries(cfg_yml)
    lock = DotyEntries(lock_yml)

    add, remove, update = compare_lock(cfg, lock)

    for r in remove:
        logger.info(f'Removing {r.name} from lock')
        lock.remove_entry(r)
    
    for a in add:
        logger.info(f'Adding {a.name} to lock')
        lock.add_entry(a)

    for u in update:
        logger.info(f'Updating {u[0].name} in lock')
        lock.remove_entry(u[0])
        lock.add_entry(u[1])

    lock.fix_all()

    with open(os.path.join(DPATH, "dotycfg.yml"), 'w') as f:
        yaml.safe_dump(cfg.get_cfg_entries(), f, sort_keys=False)

    with open(os.path.join(DPATH, "doty_lock.yml"), 'w') as f:
        yaml.safe_dump(lock.get_hashable_entries(), f, sort_keys=False)