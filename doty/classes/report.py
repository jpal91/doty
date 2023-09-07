from collections import defaultdict
import textwrap
from classes.entry import DotyEntry

class ReportItem:
    """A class representative of either 1 dotfile that would be added or removed
        or 2 dotfiles, one to be added, and one to be removed (updated)

        Based on the state of the ReportItem, it will return a string that can be used
        to print a report to the user.
    """

    def __init__(self) -> None:
        self.entry_a = None
        self.entry_b = None
    
    def add(self, val: DotyEntry) -> None:
        self.entry_b = val
    
    def rm(self, val: DotyEntry) -> None:
        self.entry_a = val
    
    @property
    def is_update(self) -> bool:
        return self.entry_a is not None and self.entry_b is not None
    
    @property
    def is_add(self) -> bool:
        return self.entry_b is not None and self.entry_a is None
    
    @property
    def is_rm(self) -> bool:
        return self.entry_a is not None and self.entry_b is None
    
    @property
    def link_report(self) -> str:
        if self.is_update:
            if self.entry_a.linked and not self.entry_b.linked:
                return f'##bred##Removed ##bwhite##link - {self.entry_a.linked_path}'
            elif not self.entry_a.linked and self.entry_b.linked:
                return f'##bgreen##Updated ##bwhite##link - {self.entry_b.name} - {self.entry_b.linked_path} -> {self.entry_b.dst}'
            else:
                return f'##bblue##Updated ##bwhite##link - {self.entry_b.name} - {self.entry_a.linked_path} -> {self.entry_b.dst}'
        elif self.is_add:
            return f'##bgreen##Added ##bwhite##link - {self.entry_b.name} - {self.entry_b.linked_path} -> {self.entry_b.dst}'
        elif self.is_rm:
            return f'##bred##Removed ##bwhite##link - {self.entry_a.name} - {self.entry_a.linked_path} -X> {self.entry_a.dst}'
    
    @property
    def file_report(self) -> str:
        if self.is_update:
            if self.entry_a.dst != self.entry_b.dst:
                return f'##bblue##Updated ##bwhite##dotfile path - {self.entry_b.name} - {self.entry_a.dst} -> {self.entry_b.dst}'
            elif self.entry_a.link_name != self.entry_b.link_name:
                return f'##bblue##Updated ##bwhite##dotfile link name - {self.entry_b.name} - {self.entry_a.link_name} -> {self.entry_b.link_name}'
            return ''
        elif self.is_add:
            return f'##bgreen##Added ##bwhite##file - {self.entry_b.name} - {self.entry_b.src} -> {self.entry_b.dst}'
        elif self.is_rm:
            return f'##bred##Removed ##bwhite##file - {self.entry_a.name} - {self.entry_a.src} <- {self.entry_a.dst}'


class ShortReport:
    """The main report class which holds all instances of Dotfiles being
        added, removed, or updated. It will collect information as the program
        updates what should or should not be in the dotfiles directory.

        Once the updating is complete, it uses the information it has collected
        to generate a report for the user, meant to be printed to the terminal.
    """

    def __init__(self) -> None:
        self.files = defaultdict(ReportItem)
        self.links = defaultdict(ReportItem)
        self.links_count = None
        self.files_count = None
    
    def __str__(self) -> str:
        if not self.links_count or not self.files_count:
            self.gen_git_report()
        
        string = f"""\

            ##bgreen##Added##end## Files: {self.files_count[0]} Links: {self.links_count[0]}
            ##bred##Removed##end## Files: {self.files_count[1]} Links: {self.links_count[1]}
            ##bblue##Updated##end## Files: {self.files_count[2]} Links: {self.links_count[2]}
        """
        return self.get_full_report() + textwrap.dedent(string)

    @property
    def changes(self) -> bool:
        return any([self.files, self.links])
    
    def add_file(self, name: str, entry: DotyEntry) -> None:
        self.files[name].add(entry)
    
    def rm_file(self, name: str, entry: DotyEntry) -> None:
        self.files[name].rm(entry)
    
    def add_link(self, name: str, entry: DotyEntry) -> None:
        self.links[name].add(entry)
    
    def rm_link(self, name: str, entry: DotyEntry) -> None:
        self.links[name].rm(entry)
    
    def gen_git_report(self) -> str:
        al, rl, ul = 0, 0, 0
        af, rf, uf = 0, 0, 0

        for v in self.links.values():
            if not v:
                continue
            
            if v.is_add:
                al += 1
            elif v.is_rm:
                rl += 1
            elif v.is_update:
                ul += 1
        
        for v in self.files.values():
            if not v:
                continue
            
            if v.is_add:
                af += 1
            elif v.is_rm:
                rf += 1
            elif v.is_update:
                uf += 1
        
        self.links_count = (al, rl, ul)
        self.files_count = (af, rf, uf)
        
        return f'Links (A{al}|R{rl}|U{ul}) | Files (A{af}|R{rf}|U{uf})'
    
    def get_full_report(self) -> str:
        report = []

        for v in self.links.values():
            if v:
                report.append(v.link_report)
        
        for v in self.files.values():
            if v:
                report.append(v.file_report)
        
        return '\n'.join(report) + '\n'

class ShortReport2:
    """The main report class which holds all instances of Dotfiles being
        added, removed, or updated. It will collect information as the program
        updates what should or should not be in the dotfiles directory.

        Once the updating is complete, it uses the information it has collected
        to generate a report for the user, meant to be printed to the terminal.
    """

    def __init__(self) -> None:
        self.files = defaultdict(ReportItem)
        self.links = defaultdict(ReportItem)
        self.links_count = None
        self.files_count = None
        
        self._report = []
        self._summary = []
        self._git_str = ''
    
    def __str__(self) -> str:
        return self.report

    @property
    def changes(self) -> bool:
        return len(self._report) > 0
    
    @property
    def report(self) -> str:
        if not self.changes:
            return '##bgreen##No changes detected##end##\n'
        return '\n'.join(self._report) + '\n' + '\n'.join(self._summary)
    
    @property
    def git_report(self) -> str:
        return self._git_str

    def add_file(self, name: str, entry: DotyEntry) -> None:
        self.files[name].add(entry)
    
    def rm_file(self, name: str, entry: DotyEntry) -> None:
        self.files[name].rm(entry)
    
    def add_link(self, name: str, entry: DotyEntry) -> None:
        self.links[name].add(entry)
    
    def rm_link(self, name: str, entry: DotyEntry) -> None:
        self.links[name].rm(entry)
    
    def gen_git_report(self, modified: int) -> None:
        al, rl, ul = 0, 0, 0
        af, rf, uf = 0, 0, 0

        for v in self.links.values():
            if not v:
                continue
            
            if v.is_add:
                al += 1
            elif v.is_rm:
                rl += 1
            elif v.is_update:
                ul += 1
        
        for v in self.files.values():
            if not v:
                continue
            
            if v.is_add:
                af += 1
            elif v.is_rm:
                rf += 1
            elif v.is_update:
                uf += 1
        
        self.links_count = (al, rl, ul)
        self.files_count = (af, rf, uf)
        self._git_str = f'Links (A{al}|R{rl}|U{ul}) | Files (A{af}|R{rf}|U{uf}|M{modified})'
        self._summary = [
            f'##bgreen##Added##end## Files: {af} Links: {al}',
            f'##bred##Removed##end## Files: {rf} Links: {rl}',
            f'##bblue##Updated##end## Files: {uf} Links: {ul}',
            f'##byellow##Modified##end## Files: {modified}'
        ]
        
        # return f'Links (A{al}|R{rl}|U{ul}) | Files (A{af}|R{rf}|U{uf})'
    
    def gen_full_report(self, git_status: dict) -> None:
        modified = 0

        for v in self.links.values():
            if v:
                self._report.append(v.link_report)
        
        for v in self.files.values():
            if v:
                self._report.append(v.file_report)
        
        for k, v in git_status.items():
            if v and v & 256:
                self._report.append(f'##byellow##Modified##end## ##bwhite##{k}')
                modified += 1
        
        self.gen_git_report(modified)
        
        # return '\n'.join(report) + '\n'

class _ShortReport:

    def __init__(self) -> None:
        self.add_files, self.rm_files, self.up_files = [], [], []
        self.add_links, self.rm_links, self.up_links = [], [], []
    
    def __str__(self):
        string = f"""\

            ##bgreen##Added##end## Files: {len(self.add_files)} Links: {len(self.add_links)}
            ##bred##Removed##end## Files: {len(self.rm_files)} Links: {len(self.rm_links)}
            ##bblue##Updated##end## Files: {len(self.up_files)} Links: {len(self.up_links)}
        """
        return self.get_full_report() + textwrap.dedent(string)
    
    @property
    def changes(self) -> bool:
        return any([self.add_files, self.rm_files, self.up_files, self.add_links, self.rm_links, self.up_links])

    def add_file(self, name: str) -> None:
        if name in self.rm_files:
            self.rm_files.remove(name)
            self.up_files.append(name)
        else:
            self.add_files.append(name)
    
    def rm_file(self, name: str) -> None:
        self.rm_files.append(name)
    
    def add_link(self, name: str) -> None:
        if name in self.rm_links:
            self.rm_links.remove(name)
            self.up_links.append(name)
        else:
            self.add_links.append(name)
    
    def rm_link(self, name: str) -> None:
        self.rm_links.append(name)
    
    def gen_git_report(self) -> str:
        return f'Links (A{len(self.add_links)}|R{len(self.rm_links)}|U{len(self.up_links)}) | Files (A{len(self.add_files)}|R{len(self.rm_files)}|U{len(self.up_files)})'
    
    def get_full_report(self) -> str:
        report = []

        for a in self.add_files:
            report.append(f'##bgreen##Added ##bwhite##File: {a}')
        
        for r in self.rm_files:
            report.append(f'##bred##Removed ##bwhite##File: {r}')
        
        for u in self.up_files:
            report.append(f'##bblue##Updated ##bwhite##File: {u}')
        
        for a in self.add_links:
            report.append(f'##bgreen##Added ##bwhite##Link: {a}')
        
        for r in self.rm_links:
            report.append(f'##bred##Removed ##bwhite##Link: {r}')
        
        for u in self.up_links:
            report.append(f'##bblue##Updated ##bwhite##Link: {u}')

        return '\n'.join(report) + '\n'


# TODO: Add a diff report for the lock file
#       Possilbe ideas - difflib, git diff, git status
#       difflib.SequenceMatcher(None, old, new), get_opcodes(), get_grouped_opcodes()

