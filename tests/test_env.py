import os
import pytest
from dotenv import dotenv_values

def test_home_dir(temp_dir):
    assert os.path.isdir(temp_dir)
    # assert os.path.isdir(temp_dir / '.config' / 'doty')
    assert os.path.isfile(temp_dir / '.bashrc')
    assert os.path.isfile(temp_dir / '.zshrc')
    assert os.path.isfile(temp_dir / '.zsh_history')
    # assert os.path.isfile(temp_dir / '.config' / 'doty' / 'dotyrc')

def test_dot_dir(temp_dir):
    assert os.path.isdir(temp_dir / 'dotfiles')
    assert os.path.isdir(temp_dir / 'dotfiles' / '.doty_config')
    # assert os.path.isfile(temp_dir / 'dotfiles' / 'dotycfg.yml')
    # assert os.path.isfile(temp_dir / 'dotfiles' / 'doty_lock.yml')
    assert os.path.isfile(temp_dir / 'dotfiles' / '.doty_config' / 'dotyrc')
    assert os.path.isfile(temp_dir / 'dotfiles' / '.doty_config' / 'dotycfg.yml')
    assert os.path.isfile(temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml')
    assert os.path.isdir(temp_dir / 'dotfiles' / 'logs')
    assert os.path.isfile(temp_dir / 'dotfiles' / 'logs' / 'doty.log')

def test_env_file(temp_dir):
    # env = dotenv_values(temp_dir / '.config' / 'doty' / 'dotyrc')
    env = dotenv_values(temp_dir / 'dotfiles' / '.doty_config' / 'dotyrc')
    assert env['DOTHOME'] == str(temp_dir)
    assert env['DOTY_DIR'] == str(temp_dir / 'dotfiles')
    assert env['DPATH'] == str(temp_dir / 'dotfiles')
    assert env['DOTY_LOG_PATH'] == str(temp_dir / 'dotfiles' / 'logs' / 'doty.log')