import os
import shutil
import yaml
from classes import DotyEntries

HOME = '/tmp/dotytest' # os.environ['HOME']
DOTDIR = os.path.join(HOME, "dotfiles") # os.environ['DOTDIR']

if 'CODESPACES' in os.environ:
    DPATH = '/workspaces/doty'
else:
    DPATH = '/home/jpal/dev/doty'

def remove_lock_entry(entry: dict) -> None:
    src, dst = entry['src'], entry['dst']

    if os.path.islink(src):
        os.unlink(src)
    
    shutil.move(dst, src)


def compare_lock(entries: dict) -> list:
    with open(os.path.join(DOTDIR, 'doty_lock.yml')) as f:
        lock = yaml.safe_load(f)
    
    for l in lock:
        name, hash = l['name'], l['hash']

        if name in entries and hash != entries[name]:
            print(f"Lock entry {name} has changed - removing...")
            remove_lock_entry(l)


def main():
    with open(os.path.join(DOTDIR, "dotycfg.yml")) as f:
        yml = yaml.safe_load(f)
    
    cfg = DotyEntries(yml)
    # cfg.fix_all()

    compare_lock(cfg.get_unlocked_hashes())

    cfg.fix_all()

    with open(os.path.join(DPATH, "dotycfg.yml"), 'w') as f:
        yaml.safe_dump(cfg.get_cfg_entries(), f, sort_keys=False)

    with open(os.path.join(DPATH, "doty_lock.yml"), 'w') as f:
        yaml.safe_dump(cfg.get_hashable_entries(), f, sort_keys=False)
    

if __name__ == "__main__":
    main()