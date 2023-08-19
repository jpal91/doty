import os
import pytest
from doty.helpers.hash import get_md5

@pytest.fixture
def good_entry():
    from doty.classes.DotyEntry import DotyEntry
    return DotyEntry({ 'name': '.bashrc' })

def good_entry_tests(good_entry, temp_dir, name, src = None, dst = None, notes = '', linked = True):
    src = str(temp_dir / name) if not src else src
    dst = str(temp_dir / 'dotfiles' / name) if not dst else dst
    hash = get_md5({ 'name': name, 'src': src, 'dst': dst, 'linked': linked })
    
    assert good_entry.name == name
    assert good_entry.src == src
    assert good_entry.dst == dst
    assert good_entry.notes == notes
    assert good_entry.linked == linked
    assert good_entry.hash == hash
    assert good_entry.is_broken_entry() == False
    assert good_entry.vals() == dict(name=name, src=src, dst=dst, notes=notes, linked=linked)
    assert good_entry.is_locked_entry() == False

def test_good_entry(good_entry, temp_dir):
    good_entry_tests(good_entry, temp_dir, '.bashrc')

def test_multi_good_entry(temp_dir):
    from doty.classes.DotyEntry import DotyEntry
    entries = [
        { 'name': '.bashrc', 'linked': False },
        { 'name': '.zshrc', 'src': str(temp_dir / '.zshrc'), 'notes': 'zshrc file' },
        { 'name': '.zsh_history', 'dst': str(temp_dir / 'dotfiles' / '.zsh_history'), 'notes': 'zsh history file', 'linked': False },
    ]

    for i, entry in enumerate(entries):
        good_entry_tests(DotyEntry(entry), temp_dir, **entries[i])

def test_prior_to_fix_good_entry_getters(good_entry):
    assert good_entry.is_correct_location() == False
    assert good_entry.is_valid_link() == False
    assert good_entry.entry_complete() == False
    assert good_entry.lock_entry() == None

def test_prior_to_fix_locations(good_entry):
    assert os.path.islink(good_entry.src) == False
    assert os.path.isfile(good_entry.dst) == False

@pytest.fixture
def good_entry_fixed(good_entry):
    good_entry.fix()
    return good_entry

def test_good_entry_fixed(good_entry_fixed, temp_dir):
    good_entry_tests(good_entry_fixed, temp_dir, '.bashrc')

def test_good_entry_fixed_getters(good_entry_fixed):
    hash_val = get_md5({ 'name': '.bashrc', 'src': good_entry_fixed.src, 'dst': good_entry_fixed.dst, 'linked': True })

    assert good_entry_fixed.is_correct_location() == True
    assert good_entry_fixed.is_valid_link() == True
    assert good_entry_fixed.entry_complete() == True
    assert good_entry_fixed.lock_entry() == dict(name='.bashrc', src=good_entry_fixed.src, dst=good_entry_fixed.dst, notes='', linked=True, hash=hash_val)

def test_good_entry_fixed_locations(good_entry_fixed):
    assert os.path.islink(good_entry_fixed.src)
    assert os.path.isfile(good_entry_fixed.dst)
    assert os.readlink(good_entry_fixed.src) == good_entry_fixed.dst


@pytest.fixture
def bad_entry():
    from doty.classes.DotyEntry import DotyEntry
    return DotyEntry({ 'name': 'bad_entry', 'linked': True })

def bad_entry_tests(bad_entry, temp_dir):
    src = str(temp_dir / 'bad_entry')
    dst = str(temp_dir / 'dotfiles' / 'bad_entry')
    hash = get_md5({ 'name': 'bad_entry', 'src': src, 'dst': dst, 'linked': False })
    
    assert bad_entry.name == 'bad_entry'
    assert bad_entry.src == src
    assert bad_entry.dst == dst
    assert bad_entry.notes == ''
    assert bad_entry.linked == False
    assert bad_entry.hash == hash
    assert bad_entry.is_broken_entry() == True
    assert bad_entry.vals() == dict(name='bad_entry', src=src, dst=dst, notes='', linked=False)
    assert bad_entry.is_locked_entry() == False

def test_bad_entry(bad_entry, temp_dir):
    bad_entry_tests(bad_entry, temp_dir)

def bad_getters(bad_entry):
    assert bad_entry.is_correct_location() == False
    assert bad_entry.is_valid_link() == False
    assert bad_entry.entry_complete() == False
    assert bad_entry.lock_entry() == None

def test_bad_prior_to_fix_getters(bad_entry):
    bad_getters(bad_entry)

def bad_locations(bad_entry):
    assert os.path.islink(bad_entry.src) == False
    assert os.path.isfile(bad_entry.dst) == False

def test_bad_prior_to_fix_locations(bad_entry):
    bad_locations(bad_entry)

@pytest.fixture
def bad_entry_fixed(bad_entry):
    bad_entry.fix()
    return bad_entry

def test_bad_entry_fixed(bad_entry_fixed, temp_dir):
    bad_entry_tests(bad_entry_fixed, temp_dir)

def test_bad_entry_fixed_getters(bad_entry_fixed):
    bad_getters(bad_entry_fixed)

def test_bad_entry_fixed_locations(bad_entry_fixed):
    bad_locations(bad_entry_fixed)


def test_undo(good_entry_fixed):
    assert good_entry_fixed.entry_complete() == True

    good_entry_fixed._locked_entry = True
    assert good_entry_fixed.undo() == True
    good_entry_fixed.run_checks()

    assert good_entry_fixed.entry_complete() == False
    assert good_entry_fixed.is_correct_location() == False
    assert good_entry_fixed.is_valid_link() == False
    assert good_entry_fixed.lock_entry() == None

    assert not os.path.islink(good_entry_fixed.src)
    assert not os.path.isfile(good_entry_fixed.dst)
    assert os.path.isfile(good_entry_fixed.src)