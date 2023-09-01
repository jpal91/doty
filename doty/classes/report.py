import textwrap
# class CustomList:

#     def __init__(self) -> None:
#         self.__list = []
    
#     def __iadd__(self, other) -> None:
#         self.__list.append(other)

#     def __isub__(self, other) -> None:
#         self.__list.remove(other)
    
#     def __contains__(self, other) -> bool:
#         return other in self.__list

class ShortReport:

    def __init__(self) -> None:
        self.add_files, self.rm_files, self.up_files = [], [], []
        self.add_links, self.rm_links, self.up_links = [], [], []
    
    def __str__(self):
        string = f"""\
            
            ##bgreen##Added##end## Files: {len(self.add_files)} Links: {len(self.add_links)}
            ##bred##Removed##end## Files: {len(self.rm_files)} Links: {len(self.rm_links)}
            ##bblue##Updated##end## Files: {len(self.up_files)} Links: {len(self.up_links)}
        """
        return textwrap.dedent(string)
    
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


# TODO: Add a diff report for the lock file
#       Possilbe ideas - difflib, git diff, git status
#       difflib.SequenceMatcher(None, old, new), get_opcodes(), get_grouped_opcodes()