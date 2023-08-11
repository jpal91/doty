import os
from datetime import datetime
from configparser import ConfigParser

class DotyProfile:
    base_cfg = {
        'meta': {
            'name': '',
            'last_updated': ''
        },
        'links': {}
    }

    def __init__(self, dot_dir: str, name: str = '') -> None:
        self.dot_dir = dot_dir
        self.dp_path = os.path.join(self.dot_dir, '.doty_profile')
        self.cfg = ConfigParser(allow_no_value=True)

        if not os.path.isfile(self.dp_path):
            self.cfg.read_dict(self.base_cfg)
            self.cfg['meta']['name'] = name
        else:
            self.cfg.read(self.dp_path)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.cfg['meta']['last_updated'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        with open(self.dp_path, 'w') as f:
            self.cfg.write(f)


# if __name__ == "__main__":
#     dp = DotyProfile('/tmp/testdir/dotfiles')

#     with dp as d:
#         d.cfg['meta']['name'] = 'test'