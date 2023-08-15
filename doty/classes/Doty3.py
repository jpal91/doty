import os
import hashlib
import json
import yaml

# IDEA: Maybe use a class to represent the config file
# IDEA: Maybe use a class to represent each file - home path, dot path, link, etc.

HOME = '/tmp/dotytest' # os.environ['HOME']
DOTDIR = os.path.join(HOME, "dotfiles") # os.environ['DOTDIR']

if os.environ['CODESPACES']:
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

        self.__dict__.update(attribs)
        self.complete_entry(attribs)
    
    def is_broken_entry(self) -> bool:
        return self._broken_entry
    
    def is_valid_link(self) -> bool:
        return self._valid_link

    def vals(self) -> dict:
        return {
            'name': self.name,
            'src': self.src,
            'dst': self.dst,
            'notes': self.notes,
        }
    
    def hashable(self) -> dict:
        if not self.is_broken_entry():
            return {
                'name': self.name,
                'src': self.src,
                'dst': self.dst,
            }
        
        return None

    def complete_entry(self, entry: dict) -> None:
        entry = { k.lower(): v for k, v in entry.items() }

        if not 'name' in entry:
            self._broken_entry = True
            return

        self.name = os.path.basename(entry['name'])

        if 'src' in entry and not os.path.isabs(entry['src']):
            self.src = os.path.join(HOME, entry['src'])
        elif not 'src' in entry:
            self.src = os.path.join(HOME, entry['name'])

        if not os.path.exists(self.src):
            print(f'Invalid entry - {self.src} does not exist')
            self._broken_entry = True
            return

        if 'dst' in entry and not os.path.isabs(entry['dst']):
            self.dst = os.path.join(DOTDIR, entry['dst'])
        elif not 'dst' in entry:
            self.dst = os.path.join(DOTDIR, entry['name'])
        
        if not 'notes' in entry:
            self.notes = ''
    
    def check_link(self) -> bool:
        if not os.path.islink(self.src) or not os.readlink(self.src) == self.dst:
            self._valid_link = False
        else:
            self._valid_link = True
        
        return self._valid_link
        


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
        return [ e.hashable() for e in self.entries ]
    
    def get_cfg_hash(self) -> str:
        return hashlib.md5(json.dumps(self.get_hashable_entries(), sort_keys=True).encode()).hexdigest()

class Doty:

    def __init__(self) -> None:
        # self.cfg = self.load_cfg()
        self.cfg = DotyEntries(self.load_cfg())
        self.cfg_changed = self.check_cfg_changes()
    
    def load_cfg(self):
        with open(os.path.join(DOTDIR, "dotycfg.yml")) as f:
            return yaml.safe_load(f)

    @property
    def cfg_hash(self):
        return self.cfg.get_cfg_hash()
    
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

        with open(os.path.join(DPATH, "doty.lock"), 'w') as f:
            f.write(self.cfg_hash)