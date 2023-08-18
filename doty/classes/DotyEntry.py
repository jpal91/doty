import os
import shutil
from helpers.hash import get_md5

# IDEA: Maybe use a class to represent the config file
# IDEA: Maybe use a class to represent each file - home path, dot path, link, etc.

HOME = os.environ['DOTHOME']
DOTDIR = os.environ['DOTY_DIR']

class DotyEntry:

    def __init__(self, attribs: dict) -> None:
        self.name = ''
        self.src = ''
        self.dst = ''
        self.notes = ''
        self.hash = ''
        self.linked = True
        self._locked_entry = False
        self._broken_entry = False
        self._valid_link = False
        self._correct_location = False

        self.__dict__.update(attribs)

        if self.hash:
            self._locked_entry = True
        
        self.run_checks()

    def __eq__(self, other) -> bool:
        return self.hash == other.hash
    
    def is_broken_entry(self) -> bool:
        return self._broken_entry
    
    def is_valid_link(self) -> bool:
        return self._valid_link
    
    def is_correct_location(self) -> bool:
        return self._correct_location
    
    def is_locked_entry(self) -> bool:
        return self._locked_entry
    
    def entry_complete(self) -> bool:
        return all([not self.is_broken_entry(), self.is_valid_link(), self.is_correct_location()])

    def vals(self) -> dict:
        return {
            'name': self.name,
            'src': self.src,
            'dst': self.dst,
            'notes': self.notes,
            'linked': self.linked,
        }
    
    def get_hash(self) -> str:
        return get_md5({ 'name': self.name, 'src': self.src, 'dst': self.dst, 'linked': self.linked })
    
    def lock_entry(self) -> dict:
        if not self.entry_complete():
            return None
        
        return {
            'name': self.name,
            'src': self.src,
            'dst': self.dst,
            'notes': self.notes,
            'linked': self.linked,
            'hash': self.hash or self.get_hash()
        }
        
    def run_checks(self) -> None:
        if not self.is_locked_entry():
            self.parse_entry()
            self.hash = self.get_hash()
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

        if entry['dst'] and not os.path.isabs(entry['dst']):
            self.dst = os.path.join(DOTDIR, entry['dst'])
        elif not entry['dst']:
            self.dst = os.path.join(DOTDIR, entry['name'])

        if not os.path.exists(self.src) and not os.path.exists(self.dst):
            print(f'Invalid entry - {self.src} does not exist')
            self._broken_entry = True
            return
        
        if not entry['notes']:
            self.notes = ''
    
    def check_link(self) -> bool:
        if self.linked:
            if not os.path.islink(self.src) or not os.readlink(self.src) == self.dst:
                self._valid_link = False
            else:
                self._valid_link = True
        else:
            if os.path.islink(self.src) and os.readlink(self.src) == self.dst:
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
        if self.linked:
            os.symlink(self.dst, self.src)
        elif os.path.islink(self.src):
            os.unlink(self.src)
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
    
    def undo(self) -> bool:
        if not self.is_locked_entry():
            return False
        
        if os.path.islink(self.src):
            os.unlink(self.src)
    
        shutil.move(self.dst, self.src)
        return True
