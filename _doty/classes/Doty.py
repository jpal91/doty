import os
import logging
from classes.DotyEntry import DotyEntry
from helpers.utils import attempt_move, attempt_link

logger = logging.getLogger('doty')

class Doty:
    HOME = os.environ['HOME']
    DOTFILES = os.path.join(os.environ['HOME'], 'dotfiles')

    def __init__(self, lock_yml: list[dict]) -> None:
        self.lock_yml = lock_yml
        self.entries = []

        self.get_entries()
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def get_entries(self) -> None:
        for entry in self.lock_yml:
            if isinstance(entry, str):
                entry = { 'name': entry }
                self.entries.append(DotyEntry(entry))
            elif isinstance(entry, dict):
                entry = { k.lower(): v for k, v in entry.items() }
                self.entries.append(DotyEntry(entry))
            else:
                logger.debug(f'Invalid entry - {entry}')
                continue
    
    def check_duplicates(self) -> None:
        name, src, dst = set(), set(), set()

        for entry in self.entries:
            if entry.name in name:
                entry.duplicate_name = True
            else:
                name.add(entry.name)
            
            if entry.src in src:
                entry.duplicate_src = True
            else:
                src.add(entry.src)
            
            if entry.dst in dst:
                entry.duplicate_dst = True
            else:
                dst.add(entry.dst)
    
    def attempt_fix_all(self) -> None:
        for entry in self.entries:
            self.attempt_fix(entry)
    
    def attempt_fix(self, entry: DotyEntry) -> None:
        if not entry.valid_name:
            entry.name = 'doty-entry' + len(self.entries)
            entry.valid_name = True
        
        if not entry.valid_src:
            entry.src = os.path.join(self.HOME, entry.name)
            entry.valid_src = True
        
        if not entry.valid_dst:
            entry.dst = os.path.join(self.DOTFILES, entry.name)
            entry.valid_dst = True

        if entry.valid_src and entry.valid_dst and not entry.correct_location:
            new_dst = attempt_move(entry.src, entry.dst)

            if new_dst:
                entry.dst = new_dst
                entry.correct_location = True
            else:
                logger.warning(f'Failed to move {entry.name} - {entry.src} -X> {entry.dst}')
                entry.correct_location = False
        
        if entry.valid_src and entry.valid_dst and entry.correct_location and not entry.valid_link:
            if attempt_link(entry.src, entry.dst):
                entry.valid_link = True
            else:
                logger.warning(f'Failed to link {entry.name} - {entry.src} -> {entry.dst}')
                entry.valid_link = False
        
        if entry.duplicate_name:
            logger.warning(f'Duplicate name - {entry.name}')
    