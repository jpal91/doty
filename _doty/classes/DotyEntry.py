import os
import logging

logger = logging.getLogger('doty')

class DotyEntry:
    DOTFILES = os.path.join(os.environ['HOME'], 'dotfiles')

    def __init__(self, entry: dict) -> None:
        self.name = ''
        self.src = ''
        self.dst = ''
        self.linked = True
        self.notes = ''

        # Internal checks
        self._valid_name = False
        self._valid_src = False
        self._valid_dst = False
        self._correct_location = False
        self._valid_link = False
        self._duplicate_name = False
        self._duplicate_src = False
        self._duplicate_dst = False

        # Set attributes
        self.__dict__.update(entry)

        # Run checks
        self.run_checks()
    
    @property
    def valid_name(self) -> bool:
        return self._valid_name
    
    @property
    def valid_src(self) -> bool:
        return self._valid_src
    
    @property
    def valid_dst(self) -> bool:
        return self._valid_dst
    
    @property
    def correct_location(self) -> bool:
        return self._correct_location
    
    @property
    def valid_link(self) -> bool:
        return self._valid_link
    
    @property
    def duplicate_name(self) -> bool:
        return self._duplicate_name
    
    @property
    def duplicate_src(self) -> bool:
        return self._duplicate_src
    
    @property
    def duplicate_dst(self) -> bool:
        return self._duplicate_dst
    
    @property
    def entry_complete(self) -> bool:
        return all([self.valid_name, self.valid_src, self.valid_dst, self.correct_location, self.valid_link])
    
    @valid_name.setter
    def valid_name(self, value: bool) -> None:
        if self.name and value:
            self._valid_name = True
        elif self.name and not value:
            logger.debug(f'Duplicate entry name - {self.name}')
            self._valid_name = False
        else:
            logger.debug('Entry name is empty')
            self._valid_name = False
    
    @valid_src.setter
    def valid_src(self, value: bool) -> None:
        if not value or not self.src:
            self._valid_src = False
        elif self.DOTFILES in self.src:
            logger.debug(f'Entry source is in the dotfiles directory - {self.name} - {self.src}')
            self._valid_src = False
        elif not os.path.isfile(self.src):
            logger.debug(f'Entry source is not a file - {self.name} - {self.src}')
            self._valid_src = False
        else:
            self._valid_src = True
    
    @valid_dst.setter
    def valid_dst(self, value: bool) -> None:
        if not value or not self.dst:
            self._valid_dst = False
        elif not self.DOTFILES in self.dst:
            logger.debug(f'Entry destination is not in the dotfiles directory - {self.name} - {self.dst}')
            self._valid_dst = False
        else:
            self._valid_dst = True
    
    @correct_location.setter
    def correct_location(self, value: bool) -> None:
        if not value:
            self._correct_location = False
        elif not os.path.isfile(self.dst):
            logger.debug(f'Entry is not in correct location - {self.name} - {self.dst}')
            self._correct_location = False
        else:
            self._correct_location = True
        
    @valid_link.setter
    def valid_link(self, value: bool) -> None:
        if not value:
            self._valid_link = False
        elif not self.linked:
            self._valid_link = True
        elif not os.path.islink(self.src) and not os.path.isfile(self.src):
            logger.debug(f'Entry is not linked back to source - {self.name} - {self.src} -X> {self.dst}')
            self._valid_link = False
        elif os.readlink(self.src) != self.dst:
            logger.debug(f'Entry is not linked back to source - {self.name} - {self.src} -X> {self.dst}')
            self._valid_link = False
        else:
            self._valid_link = True
    
    @duplicate_name.setter
    def duplicate_name(self, value: bool) -> None:
        self._duplicate_name = value
    
    @duplicate_src.setter
    def duplicate_src(self, value: bool) -> None:
        self._duplicate_src = value
    
    @duplicate_dst.setter
    def duplicate_dst(self, value: bool) -> None:
        self._duplicate_dst = value
    
    def run_checks(self) -> None:
        self.valid_name = True
        self.valid_src = True
        self.valid_dst = True
        self.correct_location = True
        self.valid_link = True
    
    def diagnose(self) -> None:
        logger.setLevel(logging.DEBUG)
        logger.debug(f'Entry name: {self.name}')
        self.run_checks()

        if self.duplicate_name:
            logger.debug('Duplicate entry name')
        if self.duplicate_src:
            logger.debug('Duplicate entry source')
        if self.duplicate_dst:
            logger.debug('Duplicate entry destination')

        logger.setLevel(logging.INFO)
        