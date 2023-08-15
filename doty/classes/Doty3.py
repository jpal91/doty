import os
import hashlib
import json
import yaml

# IDEA: Maybe use a class to represent the config file
# IDEA: Maybe use a class to represent each file - home path, dot path, link, etc.

HOME = '/tmp/dotytest' # os.environ['HOME']
DOTDIR = os.path.join(HOME, "dotfiles") # os.environ['DOTDIR']

class DotyEntry:

    def __init__(self, attribs: dict) -> None:
        self.name = ''
        self.src = ''
        self.dst = ''
        self.notes = ''
        self.broken = False

        self.__dict__.update(attribs)
        self.complete_entry(attribs)
    
    def is_broken(self):
        return self.broken

    def vals(self):
        return {
            'name': self.name,
            'src': self.src,
            'dst': self.dst,
            'notes': self.notes,
        }
    
    def hashable(self):
        if not self.broken:
            return {
                'name': self.name,
                'src': self.src,
                'dst': self.dst,
            }
        else:
            return None

    def complete_entry(self, entry: dict):
        entry = { k.lower(): v for k, v in entry.items() }

        if not 'name' in entry:
            self.broken = True
            return
        else:
            self.name = entry['name']
        
        if 'src' in entry and not os.path.isabs(entry['src']):
            self.src = os.path.join(HOME, entry['src'])

            if not os.path.exists(self.src):
                print(f'Invalid entry - {self.src} does not exist')
                self.broken = True
                return None
            
        if 'dst' in entry and not os.path.isabs(entry['dst']):
            self.dst = os.path.join(DOTDIR, entry['dst'])

        if not 'src' in entry:
            self.src = os.path.join(HOME, self.name)

            if not os.path.exists(self.src):
                print(f'Invalid entry - {self.src} does not exist')
                self.broken = True
                return None
            
        if not 'dst' in entry:
            self.dst = os.path.join(DOTDIR, self.name)
        if not 'notes' in entry:
            self.notes = ''
        


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

            if updated_item.is_broken():
                print(f'Cannot parse entry - {item}')
                continue

            new_cfg.append(updated_item)
        
        return new_cfg
    
    def get_entries(self) -> list:
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
    def entries(self):
        return self.cfg.get_entries()
    
    def check_cfg_changes(self):
        lock_file = os.path.join(DOTDIR, "doty.lock")
        if not os.path.isfile(lock_file):
            return True
        
        with open(lock_file) as f:
            lock = f.read()
        
        return lock != self.cfg_hash

    # def hash_entry(self, entry: list):
    #     entry = entry.copy()
    #     for e in entry:
    #         if 'notes' in e:
    #             del e['notes']

    #     return hashlib.md5(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    
    # def complete_entry(self, entry: dict):
    #     entry = { k.lower(): v for k, v in entry.items() }
    #     doty_entry = {
    #         'name': '',
    #         'src': '',
    #         'dst': '',
    #         'notes': '',
    #     }

    #     if not 'name' in entry:
    #         print('Invalid entry - missing name')
    #         return None
    #     else:
    #         doty_entry['name'] = entry['name']
        
    #     if 'src' in entry and not os.path.isabs(entry['src']):
    #         doty_entry['src'] = os.path.join(HOME, entry['src'])

    #         if not os.path.exists(entry['src']):
    #             print(f'Invalid entry - {entry["src"]} does not exist')
    #             return None
            
    #     if 'dst' in entry and not os.path.isabs(entry['dst']):
    #         doty_entry['dst'] = os.path.join(DOTDIR, entry['dst'])

    #     if not 'src' in entry:
    #         doty_entry['src'] = os.path.join(HOME, doty_entry['name'])

    #         if not os.path.exists(entry['src']):
    #             print(f'Invalid entry - {entry["src"]} does not exist')
    #             return None
            
    #     if not 'dst' in entry:
    #         doty_entry['dst'] = os.path.join(DOTDIR, doty_entry['name'])
    #     if not 'notes' in entry:
    #         doty_entry['notes'] = ''
        
    #     return doty_entry

    # def check_valid(self):
    #     new_cfg = []

    #     for item in self.cfg:
    #         if isinstance(item, str):
    #             new_item = {
    #                 'name': item,
    #             }
    #             updated_item = self.complete_entry(new_item)
    #         elif isinstance(item, dict):
    #             updated_item = self.complete_entry(item)
    #         else:
    #             print(f'Invalid entry - {item}')
    #             continue

    #         if not updated_item:
    #             print(f'Cannot parse entry - {item}')
    #             continue
            
    #         new_cfg.append(updated_item)
        
    #     self.cfg = new_cfg
    
    def write_cfg(self):
        with open(os.path.join('/home/jpal/dev/doty', "dotycfg.yml"), 'w') as f:
            yaml.safe_dump(self.entries, f, sort_keys=False)

        with open(os.path.join('/home/jpal/dev/doty', "doty.lock"), 'w') as f:
            f.write(self.cfg_hash)