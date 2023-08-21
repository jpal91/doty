import os
import pytest
from dotenv import dotenv_values
from doty.init import main

@pytest.fixture(scope='module')
def init_dir(tmp_path_factory):
    temp = tmp_path_factory.mktemp('init_dir')
    main(alt_home=str(temp))
    return temp

def test_dirs_created(init_dir):
    assert os.path.isdir(init_dir / 'dotfiles')
    assert os.path.isdir(init_dir / 'dotfiles' / 'logs')
    assert os.path.isdir(init_dir / 'dotfiles' / '.doty_config')

def test_files_created(init_dir):
    assert os.path.isfile(init_dir / 'dotfiles' / '.doty_config' / 'dotycfg.yml')
    assert os.path.isfile(init_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml')
    assert os.path.isfile(init_dir / 'dotfiles' / '.doty_config' / 'dotyrc')
    assert os.path.isfile(init_dir / 'dotfiles' / 'logs' / 'doty.log')

def test_env_file(init_dir):
    env_path = init_dir / 'dotfiles' / '.doty_config' / 'dotyrc'
    values = dotenv_values(env_path)

    assert values['DOTHOME'] == str(init_dir)
    assert values['DOTY_DIR'] == str(init_dir / 'dotfiles')
    assert values['DOTY_LOG_PATH'] == str(init_dir / 'dotfiles' / 'logs' / 'doty.log')