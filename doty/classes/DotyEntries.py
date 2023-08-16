from classes.DotyEntry import DotyEntry

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
    
    def fix_all(self) -> bool:
        [ e.fix() for e in self.entries ]
        return True
    
    def add_entry(self, entry: DotyEntry) -> None:
        if not isinstance(entry, DotyEntry):
            raise TypeError('Entry must be a DotyEntry object')
        self.entries.append(entry)
    
    def remove_entry(self, entry: DotyEntry) -> None:
        if not isinstance(entry, DotyEntry):
            raise TypeError('Entry must be a DotyEntry object')
        entry.undo()
        self.entries.remove(entry)
    