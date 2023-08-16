import os
import yaml
from classes import DotyEntries

HOME = os.environ['DOTHOME']
DOTDIR = os.environ['DOTY_DIR']
DPATH = os.environ['DPATH']

def compare_lock(cfg_entries: DotyEntries, lock_entries: DotyEntries) -> tuple:
    print('Running initial checks and detecting changes...\n')

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

    print(f'Adding {insert} entries\nRemoving {delete} entries\nUpdating {upd} entries\nNo change to {no_change} entries\n')

    return add, remove, update

def main():
    with open(os.path.join(DOTDIR, "dotycfg.yml")) as f:
        cfg_yml = yaml.safe_load(f)

    with open(os.path.join(DOTDIR, 'doty_lock.yml')) as f:
        lock_yml = yaml.safe_load(f)
    
    cfg = DotyEntries(cfg_yml)
    lock = DotyEntries(lock_yml)

    add, remove, update = compare_lock(cfg, lock)

    for r in remove:
        print(f'Removing {r.name} from lock')
        lock.remove_entry(r)
    
    for a in add:
        print(f'Adding {a.name} to lock')
        lock.add_entry(a)
    
    for u in update:
        print(f'Updating {u[0].name} in lock')
        lock.remove_entry(u[0])
        lock.add_entry(u[1])
    
    lock.fix_all()

    with open(os.path.join(DPATH, "dotycfg.yml"), 'w') as f:
        yaml.safe_dump(cfg.get_cfg_entries(), f, sort_keys=False)

    with open(os.path.join(DPATH, "doty_lock.yml"), 'w') as f:
        yaml.safe_dump(lock.get_hashable_entries(), f, sort_keys=False)