import os
import pytest
from unittest.mock import patch

@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    home = tmp_path_factory.mktemp('dotytmp')
    dotfiles = home / 'dotfiles'
    dotfiles.mkdir()
    doty_config = dotfiles / '.doty_config'
    doty_config.mkdir()
    doty_lock = doty_config / 'doty_lock.yml'
    doty_lock.touch()

    for i in range(5):
        entry = home / f'.good_entry{i}'
        entry.touch()
    
    return home

# @pytest.fixture(autouse=True)
# def setup(temp_dir):
#     # with patch.dict(os.environ, {'HOME': str(temp_dir)}):
#     #     yield
#     os.environ.update({'HOME': str(temp_dir)})

