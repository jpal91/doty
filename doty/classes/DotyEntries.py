import logging
from classes.DotyEntry import DotyEntry

logger = logging.getLogger('doty')

class DotyEntries:

    def __init__(self, entries: list) -> None:
        self.entries = self.check_valid(entries)

    def check_valid(self, entries: list) -> list[DotyEntry]:
        new_cfg = []

        if not entries:
            return new_cfg

        for item in entries:
            if isinstance(item, str):
                updated_item = DotyEntry({ 'name': item })
            elif isinstance(item, dict):
                updated_item = DotyEntry(item)
            else:
                logger.debug(f'Invalid entry - {item}')
                continue

            if updated_item.is_broken_entry():
                logger.debug(f'Cannot parse entry - {item}')

            new_cfg.append(updated_item)
        
        return new_cfg

    def get_cfg_entries(self) -> list:
        return [ e.vals() for e in self.entries ]
    
    def get_hashable_entries(self) -> list:
        return [ e.lock_entry() for e in self.entries if e.entry_complete() ]
    
    def fix_all(self) -> bool:
        [ e.fix() for e in self.entries ]
        return True
    
    def add_entry(self, entry: DotyEntry) -> None:
        entry.run_checks()
        logger.debug(f'Adding Entry - {entry.__dict__}')
        self.entries.append(entry)
    
    def remove_entry(self, entry: DotyEntry) -> None:
        entry.undo()
        self.entries.remove(entry)
    