import os
import pytest

@pytest.fixture
def doty_entries(temp_dir):
    from doty.classes.DotyEntries import DotyEntries
    entries = [
        { 'name': '.bashrc', 'linked': False },
        { 'name': '.zshrc', 'src': str(temp_dir / '.zshrc'), 'notes': 'zshrc file' },
        { 'name': '.zsh_history', 'dst': str(temp_dir / 'dotfiles' / '.zsh_history'), 'notes': 'zsh history file', 'linked': False },
        { 'name': '.bad_entry', 'linked': True }
    ]

    doty_entries = DotyEntries(entries)
    return doty_entries
    

@pytest.fixture
def doty_entries_fixed(doty_entries):
    doty_entries.fix_all()
    yield doty_entries
    
    for e in doty_entries.entries:
        if not e.entry_complete():
            continue
        e._locked_entry = True
        e.undo()

def test_doty_entries(doty_entries):
    assert len(doty_entries.entries) == 4
    assert doty_entries.entries[0].name == '.bashrc'
    assert doty_entries.entries[1].name == '.zshrc'
    assert doty_entries.entries[2].name == '.zsh_history'
    assert doty_entries.entries[3].name == '.bad_entry'

    assert len(doty_entries.get_cfg_entries()) == 4
    assert len(doty_entries.get_hashable_entries()) == 0


def test_doty_entries_fixed(doty_entries_fixed):
    assert len(doty_entries_fixed.entries) == 4
    assert doty_entries_fixed.entries[0].name == '.bashrc'
    assert doty_entries_fixed.entries[1].name == '.zshrc'
    assert doty_entries_fixed.entries[2].name == '.zsh_history'
    assert doty_entries_fixed.entries[3].name == '.bad_entry'

    assert len(doty_entries_fixed.get_cfg_entries()) == 4
    assert len(doty_entries_fixed.get_hashable_entries()) == 3

def test_doty_entries_remove_bad_entry(doty_entries_fixed):
    assert len(doty_entries_fixed.entries) == 4
    doty_entries_fixed.remove_entry(doty_entries_fixed.entries[3])
    assert len(doty_entries_fixed.entries) == 3
    assert doty_entries_fixed.entries[0].name == '.bashrc'
    assert doty_entries_fixed.entries[1].name == '.zshrc'
    assert doty_entries_fixed.entries[2].name == '.zsh_history'
    assert len(doty_entries_fixed.get_cfg_entries()) == 3
    assert len(doty_entries_fixed.get_hashable_entries()) == 3

def test_doty_entries_remove_good_entry(doty_entries_fixed):
    assert len(doty_entries_fixed.entries) == 4
    doty_entries_fixed.remove_entry(doty_entries_fixed.entries[0])
    assert len(doty_entries_fixed.entries) == 3
    assert doty_entries_fixed.entries[0].name == '.zshrc'
    assert doty_entries_fixed.entries[1].name == '.zsh_history'
    assert doty_entries_fixed.entries[2].name == '.bad_entry'
    assert len(doty_entries_fixed.get_cfg_entries()) == 3
    assert len(doty_entries_fixed.get_hashable_entries()) == 2

def test_doty_entries_add_entry(doty_entries_fixed, temp_dir):
    from doty.classes.DotyEntry import DotyEntry
    (temp_dir / '.good_entry').touch()
    
    entry = DotyEntry({ 'name': '.good_entry' })
    entry.fix()
    doty_entries_fixed.add_entry(entry)
    
    assert len(doty_entries_fixed.entries) == 5
    assert doty_entries_fixed.entries[0].name == '.bashrc'
    assert doty_entries_fixed.entries[1].name == '.zshrc'
    assert doty_entries_fixed.entries[2].name == '.zsh_history'
    assert doty_entries_fixed.entries[3].name == '.bad_entry'
    assert doty_entries_fixed.entries[4].name == '.good_entry'
    assert len(doty_entries_fixed.get_cfg_entries()) == 5
    assert len(doty_entries_fixed.get_hashable_entries()) == 4
    assert doty_entries_fixed.entries[4].entry_complete() == True