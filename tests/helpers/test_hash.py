import os
import pytest
from doty.helpers.hash import get_md5

def first_entry():
    return {
        'name': '.bashrc',
        'src': '/home/username/.bashrc',
        'dst': '/home/username/dotfiles/.bashrc',
    }

def second_entry():
    return {
        'name': '.zshrc',
        'src': '/home/username/.zshrc',
        'dst': '/home/username/dotfiles/.zshrc',
    }

def first_entry_small_change():
    return {
        'name': '.bashrc',
        'src': '/home/username/.bashrc',
        'dst': '/home/username/dotfiles/bash/.bashrc',
    }

def test_equal_entries():
    entry1 = first_entry()
    entry2 = first_entry()

    assert get_md5(entry1) == get_md5(entry2)

def test_different_entries():
    entry1 = first_entry()
    entry2 = second_entry()

    assert get_md5(entry1) != get_md5(entry2)

def test_equal_entries_with_small_change():
    entry1 = first_entry()
    entry2 = first_entry_small_change()

    assert get_md5(entry1) != get_md5(entry2)

# def test_env_with_env(env):
#     assert os.getenv('DOTHOME') == '/home/username'
#     assert os.getenv('DOTDIR') == '/home/username/dotfiles'
#     assert os.getenv('DPATH') == '/home/username/dotfiles/.config/doty'
#     assert os.getenv('DOTY_LOG_PATH') == '/home/username/dotfiles/.config/doty/doty.log'