import os
import pytest
from _doty.update import link_new_files, update

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({'HOME': str(temp_dir)})

def test_link_new_files(temp_dir):
    df_links = [str(temp_dir / 'dotfiles' / 'dot_dir' / 'dot_file4')]
    
    assert not os.path.islink(str(temp_dir / 'dot_file4'))
    link_new_files(df_links)
    assert os.path.islink(str(temp_dir / 'dot_file4'))
    os.unlink(str(temp_dir / 'dot_file4'))

def test_update(temp_dir):
    assert not os.path.islink(str(temp_dir / 'dot_file4'))
    update()
    assert os.path.islink(str(temp_dir / 'dot_file4'))
