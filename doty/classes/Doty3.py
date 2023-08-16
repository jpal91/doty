import os
import shutil
import hashlib
import json
import yaml
from helpers.hash import get_md5

# IDEA: Maybe use a class to represent the config file
# IDEA: Maybe use a class to represent each file - home path, dot path, link, etc.

HOME = '/tmp/dotytest' # os.environ['HOME']
DOTDIR = os.path.join(HOME, "dotfiles") # os.environ['DOTDIR']

if 'CODESPACES' in os.environ:
    DPATH = '/workspaces/doty'
else:
    DPATH = '/home/jpal/dev/doty'

class DotyEntry:

    def __init__(self, attribs: dict) -> None:
        self.name = ''
        self.src = ''
        self.dst = ''
        self.notes = ''
        self._broken_entry = False
        self._valid_link = False
        self._correct_location = False

        self.__dict__.update(attribs)
        self.run_checks()

    
    def is_broken_entry(self) -> bool:
        return self._broken_entry
    
    def is_valid_link(self) -> bool:
        return self._valid_link
    
    def is_correct_location(self) -> bool:
        return self._correct_location
    
    def entry_complete(self) -> bool:
        return all([not self._broken_entry, self._valid_link, self._correct_location])

    def vals(self) -> dict:
        return {
            'name': self.name,
            'src': self.src,
            'dst': self.dst,
            'notes': self.notes,
        }
    
    def get_hash(self) -> str:
        return get_md5({ 'name': self.name, 'src': self.src, 'dst': self.dst })
    
    def lock_entry(self) -> dict:
        if not self.entry_complete():
            return None
        
        return {
            'name': self.name,
            'src': self.src,
            'dst': self.dst,
            'notes': self.notes,
            'hash': self.get_hash()
        }
        
    def run_checks(self) -> None:
        self.parse_entry()
        self.check_link()
        self.check_location()

    def parse_entry(self) -> None:
        entry = { k.lower(): v for k, v in self.__dict__.items() }

        if not 'name' in entry:
            self._broken_entry = True
            return

        self.name = os.path.basename(entry['name'])

        if entry['src'] and not os.path.isabs(entry['src']):
            self.src = os.path.join(HOME, entry['src'])
        elif not entry['src']:
            self.src = os.path.join(HOME, entry['name'])

        if not os.path.exists(self.src):
            print(f'Invalid entry - {self.src} does not exist')
            self._broken_entry = True
            return

        if entry['dst'] and not os.path.isabs(entry['dst']):
            self.dst = os.path.join(DOTDIR, entry['dst'])
        elif not entry['dst']:
            self.dst = os.path.join(DOTDIR, entry['name'])
        
        if not entry['notes']:
            self.notes = ''
    
    def check_link(self) -> bool:
        if not os.path.islink(self.src) or not os.readlink(self.src) == self.dst:
            self._valid_link = False
        else:
            self._valid_link = True
        
        return self._valid_link
    
    def check_location(self) -> bool:
        if not os.path.isfile(self.dst):
            self._correct_location = False
        else:
            self._correct_location = True
        
        return self._correct_location
    
    def fix_location(self) -> bool:
        attempted = False

        while True:
            try:
                shutil.move(self.src, self.dst)
            except FileNotFoundError:
                if attempted:
                    return False
                os.makedirs(os.path.dirname(self.dst))
                attempted = True
            else:
                return self.check_location()
    
    def fix_link(self) -> bool:
        os.symlink(self.dst, self.src)
        return self.check_link()
    
    def fix(self) -> bool:
        if self.entry_complete():
            return True
        
        if self.is_broken_entry():
            return False
        
        if not self.is_correct_location() and not self.fix_location():
            return False
        
        if not self.is_valid_link() and not self.fix_link():
            return False
        
        return True


class DotyEntries:

    def __init__(self, entries: list) -> None:
        self.entries = self.check_valid(entries)

    def check_valid(self, entries: list) -> list[DotyEntry]:
        new_cfg = []

        for item in entries:
            if isinstance(item, str):
                updated_item = DotyEntry({ 'name': item })
            elif isinstance(item, dict):
                updated_item = DotyEntry(item)
            else:
                print(f'Invalid entry - {item}')
                continue

            if updated_item.is_broken_entry():
                print(f'Cannot parse entry - {item}')

            new_cfg.append(updated_item)
        
        return new_cfg

    def get_cfg_entries(self) -> list:
        return [ e.vals() for e in self.entries ]
    
    def get_hashable_entries(self) -> list:
        return [ e.lock_entry() for e in self.entries if e.entry_complete() ]
    
    def get_unlocked_hashes(self) -> dict:
        return { e.name: e.get_hash() for e in self.entries }
    
    def fix_all(self) -> bool:
        [ e.fix() for e in self.entries ]
        return True
    
    # def get_cfg_hash(self) -> str:
    #     return hashlib.md5(json.dumps(self.get_hashable_entries(), sort_keys=True).encode()).hexdigest()

class Doty:

    def __init__(self) -> None:
        # self.cfg = self.load_cfg()
        self.cfg = DotyEntries(self.load_cfg())
        self.cfg.fix_all()
        # self.cfg_changed = self.check_cfg_changes()
    
    def load_cfg(self):
        with open(os.path.join(DOTDIR, "dotycfg.yml")) as f:
            return yaml.safe_load(f)

    @property
    def cfg_hash(self):
        return self.cfg.get_hashable_entries()
    
    @property
    def cfg_entries(self):
        return self.cfg.get_cfg_entries()
    
    def check_cfg_changes(self):
        lock_file = os.path.join(DOTDIR, "doty.lock")
        if not os.path.isfile(lock_file):
            return True
        
        with open(lock_file) as f:
            lock = f.read()
        
        return lock != self.cfg_hash
    
    def write_cfg(self):
        with open(os.path.join(DPATH, "dotycfg.yml"), 'w') as f:
            yaml.safe_dump(self.cfg_entries, f, sort_keys=False)

        with open(os.path.join(DPATH, "doty_lock.yml"), 'w') as f:
            yaml.safe_dump(self.cfg_hash, f, sort_keys=False)