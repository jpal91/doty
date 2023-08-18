import os
import logging
import yaml
from classes import DotyEntries

HOME = os.environ["DOTHOME"]
DOTDIR = os.environ["DOTY_DIR"]
DPATH = os.environ["DPATH"]

logger = logging.getLogger('doty')

def get_entries(
    yml: list, linked: range(3), name: str = "", broken: bool = False
) -> list:
    targets = []
    entries = DotyEntries(yml)

    for entry in entries.entries:
        if name and name not in entry.name:
            continue

        if broken:
            if entry.is_broken_entry():
                targets.append(entry)
            continue
        
        if linked == 0:
            targets.append(entry)
        elif linked == 1 and entry.linked:
            targets.append(entry)
        elif linked == 2 and not entry.linked:
            targets.append(entry)

    return targets


def main(args) -> None:

    with open(os.path.join(DOTDIR, "dotycfg.yml")) as f:
        cfg_yml = yaml.safe_load(f)

    with open(os.path.join(DOTDIR, "doty_lock.yml")) as f:
        lock_yml = yaml.safe_load(f)

    if not cfg_yml and not lock_yml:
        logger.warning("dotycfg.yml is empty, please add entries to it")
        return

    targets = []

    if args.list_lvl in [0, 2]:
        locked_targets = get_entries(
            lock_yml, 
            linked=args.l or args.N or 0,
            name=args.e
        )

        if args.list_lvl == 2:
            targets.append("Locked entries:")

        targets.extend(locked_targets)
    
    if args.list_lvl in [1, 2, 3]:
        cfg_targets = get_entries(
            cfg_yml, 
            linked=args.l or args.N or 0,
            name=args.e,
            broken=True if args.list_lvl == 3 else False
        )

        if args.list_lvl == 2:
            targets.append("Config entries:")

        targets.extend(cfg_targets)
    
    [logger.info(t) for t in targets] if targets else logger.info('No entries matched your search!')
