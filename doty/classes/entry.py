import os
import textwrap
from doty.classes.logger import DotyLogger

logger = DotyLogger()

class DotyEntry:
    """A class to represent an entry in a doty_lock file."""

    def __init__(self, vals: dict) -> None:
        self.name = ''
        self.src = ''
        self.dst = ''
        self.linked = True
        self.link_name = ''

        self.__dict__.update(vals)
        self.extrapolate()

    def __eq__(self, other) -> bool:
        return self.dict == other.dict
    
    def __contains__(self, other) -> bool:
        return self.dict == other.dict

    def __str__(self) -> str:
        string = f"""\
        ##bblue##Name: ##bwhite##{self.name}
        ##bblue##Source: ##bwhite##{self.src}
        ##bblue##Destination: ##bwhite##{self.dst}
        ##bblue##Linked: ##bwhite##{self.linked}
        ##bblue##Link Name: ##bwhite##{self.link_name}
        
        """
        return textwrap.dedent(string)
    
    @property
    def dict(self) -> dict:
        """Return the values of the entry."""
        return {
            'name': self.name,
            'src': self.src,
            'dst': self.dst,
            'linked': self.linked,
            'link_name': self.link_name
        }
    
    def extrapolate(self) -> None:
        """Fill in the missing values of the entry."""

        if not self.name and not self.src:
            logger.debug('##bred##Entry is missing name and src. Aborting...')
            return
        elif not self.name:
            self.name = os.path.basename(self.src)
        
        logger.debug(f'Extrapolating entry: {self.name}')

        if not self.src:
            logger.debug(f'Adding src for {self.name}')
            self.src = os.path.join(os.environ['HOME'], self.name)
        
        if not self.dst:
            logger.debug(f'Adding dst for {self.name}')
            self.dst = os.path.join(os.environ['HOME'], 'dotfiles', self.name)
        
        if not self.link_name:
            logger.debug(f'Adding link_name for {self.name}')
            self.link_name = self.name
        
        logger.debug(f'Extrapolated entry: {self.name} - {self.dict}')

if __name__ == '__main__':
    dict1 = { 'name': 'bashrc', 'src': '/home/user/bashrc', 'dst': '/home/user/dotfiles/bashrc', 'linked': True, 'link_name': 'bashrc' }
    dict2 = { 'name': 'bashrc', 'src': '/home/user/bashrc', 'dst': '/home/user/dotfiles/bashrc', 'linked': True, 'link_name': 'bashrc' }
    dict3 = { 'name': 'zshrc', 'src': '/home/user/zshrc', 'dst': '/home/user/dotfiles/zshrc', 'linked': True, 'link_name': 'zshrc' }
    dict4 = { 'name': 'wshrc', 'src': '/home/user/wshrc', 'dst': '/home/user/dotfiles/wshrc', 'linked': True, 'link_name': 'wshrc' }

    entry1 = DotyEntry(dict1)
    entry2 = DotyEntry(dict2)
    entry3 = DotyEntry(dict3)
    entry4 = DotyEntry(dict4)

    arr1 = [entry2, entry3, entry4]
    arr2 = [entry1]

    print([entry.name for entry in arr1 if entry in arr2])