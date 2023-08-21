import os
import pytest
from doty.helpers.hash import get_md5

# @pytest.fixture
# def good_entry():
#     from doty.classes.DotyEntry import DotyEntry
#     return DotyEntry({ 'name': '.bashrc' })

@pytest.fixture(scope='module')
def entries_dicts(temp_dir):
    return [
        { 'name': '.bashrc', 'linked': False }, # Unlinked
        { 'name': '.zshrc', 'dst': str(temp_dir / 'dotfiles' / 'zshrc.zsh'), 'notes': 'zshrc file' }, # Test with different dst name
        { 'name': '.zsh_history', 'dst': str(temp_dir / 'dotfiles' / 'zsh') + '/', 'notes': 'zsh history file' }, # No file name, trailing slash dst
        { 'name': 'wget', 'src': str(temp_dir / '.wgetrc'), 'notes': 'wgetrc file' }, # "name" different from src
    ]

@pytest.fixture(scope='module')
def good_entries(entries_dicts):
    from doty.classes.DotyEntry import DotyEntry
    return [ DotyEntry(entry) for entry in entries_dicts ]

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

    assert good_entry.is_correct_location() == False
    assert good_entry.entry_complete() == False
    assert good_entry.lock_entry() == None

    if not linked:
        assert good_entry.is_valid_link() == True
    else:
        assert good_entry.is_valid_link() == False

    assert os.path.islink(good_entry.src) == False
    assert os.path.isfile(good_entry.dst) == False

def test_good_entries_pre_fix(temp_dir, good_entries, entries_dicts):
    for i, entry in enumerate(good_entries):
        good_entry_tests(entry, temp_dir, **entries_dicts[i])

@pytest.fixture(scope='module')
def good_fixed_entries(good_entries):
    [ entry.fix() for entry in good_entries ]
    return good_entries

def test_good_post_fix_entry_0(temp_dir, good_fixed_entries, entries_dicts):
    # .bashrc
    entry = good_fixed_entries[0]
    entry_dict = entries_dicts[0]
    dotfiles = temp_dir / 'dotfiles'

    assert entry.name == entry_dict['name']
    assert entry.linked == False
    assert entry.entry_complete() == True
    assert not os.path.isfile(entry.src)
    assert os.path.isfile(entry.dst)
    assert not os.path.islink(entry.src)
    assert entry.dst == str(dotfiles / entry_dict['name'])

def test_good_post_fix_entry_1(good_fixed_entries, entries_dicts):
    # .zshrc
    entry = good_fixed_entries[1]
    entry_dict = entries_dicts[1]

    assert entry.name == entry_dict['name']
    assert entry.entry_complete() == True
    assert os.path.isfile(entry.dst)
    assert os.path.islink(entry.src)
    assert os.readlink(entry.src) == entry.dst
    assert entry.name != os.path.basename(entry.dst)
    assert entry.dst == entry_dict['dst']

def test_good_post_fix_entry_2(good_fixed_entries, entries_dicts):
    # .zsh_history
    entry = good_fixed_entries[2]
    entry_dict = entries_dicts[2]

    assert entry.name == entry_dict['name']
    assert entry.entry_complete() == True
    assert os.path.isfile(entry.dst)
    assert os.path.islink(entry.src)
    assert os.readlink(entry.src) == entry.dst
    assert entry.name == os.path.basename(entry.dst)
    assert entry.dst != entry_dict['dst']
    assert entry.dst == entry_dict['dst'] + entry.name

def test_good_post_fix_entry_3(good_fixed_entries, entries_dicts):
    # wget
    entry = good_fixed_entries[3]
    entry_dict = entries_dicts[3]

    assert entry.name == entry_dict['name']
    assert entry.entry_complete() == True
    assert os.path.isfile(entry.dst)
    assert os.path.islink(entry.src)
    assert os.readlink(entry.src) == entry.dst
    assert entry.name == os.path.basename(entry.dst)
    assert entry.name != os.path.basename(entry.src)

def test_undo(good_fixed_entries):
    for e in good_fixed_entries:
        assert e.entry_complete() == True

        e._locked_entry = True
        assert e.undo() == True
        e.run_checks()

        assert e.entry_complete() == False
        assert e.is_correct_location() == False
        assert e.lock_entry() == None

        assert not os.path.islink(e.src)
        assert not os.path.isfile(e.dst)
        assert os.path.isfile(e.src)

@pytest.fixture(scope='module')
def bad_entry_dicts(temp_dir):
    return [
        { 'bad_key': 'val', 'another_bad_key': 'val' }, # No valid name
        { 'name': '.bashrc', 'src': str(temp_dir / 'bashr'), 'dst': str(temp_dir / 'dotfiles' / '.bashrc') }, # File doesn't exist
        { 'name': '.zshrc', 'src': str(temp_dir / '.zshrc'), 'dst': str(temp_dir / '.config' / '.zshrc') }, # File exists, but dst not valid
    ]

@pytest.fixture(scope='module')
def bad_entries(bad_entry_dicts):
    from doty.classes.DotyEntry import DotyEntry
    return [ DotyEntry(entry) for entry in bad_entry_dicts ]

def test_bad_entry_0(bad_entries):
    entry = bad_entries[0]

    assert entry.name == ''
    assert entry.is_broken_entry() == True
    assert entry.entry_complete() == False

    entry.fix()

    assert entry.is_broken_entry() == True
    assert entry.entry_complete() == False
    assert entry.lock_entry() == None

def test_bad_entry_1(bad_entries, bad_entry_dicts):
    entry = bad_entries[1]
    entry_dict = bad_entry_dicts[1]

    assert entry.name == entry_dict['name']
    assert entry.src == entry_dict['src']
    assert entry.dst == entry_dict['dst']
    assert entry.is_broken_entry() == True
    assert entry.entry_complete() == False

    entry.fix()

    assert entry.is_broken_entry() == True
    assert entry.entry_complete() == False
    assert entry.lock_entry() == None

def test_bad_entry_2(bad_entries, bad_entry_dicts):
    entry = bad_entries[2]
    entry_dict = bad_entry_dicts[2]

    assert entry.name == entry_dict['name']
    assert entry.src == entry_dict['src']
    assert entry.dst == entry_dict['dst']
    assert entry.is_broken_entry() == True
    assert entry.entry_complete() == False

    entry.fix()

    assert entry.is_broken_entry() == True
    assert entry.entry_complete() == False
    assert entry.lock_entry() == None

# def test_good_entry(good_entry, temp_dir):
#     good_entry_tests(good_entry, temp_dir, '.bashrc')

# def test_multi_good_entry(temp_dir):
#     from doty.classes.DotyEntry import DotyEntry
#     entries = [
#         { 'name': '.bashrc', 'linked': False },
#         { 'name': '.zshrc', 'src': str(temp_dir / '.zshrc'), 'notes': 'zshrc file' },
#         { 'name': '.zsh_history', 'dst': str(temp_dir / 'dotfiles' / 'zsh' / '.zsh_history'), 'notes': 'zsh history file', 'linked': False },
#     ]

#     for i, entry in enumerate(entries):
#         good_entry_tests(DotyEntry(entry), temp_dir, **entries[i])

# def test_prior_to_fix_good_entry_getters(good_entry):
#     assert good_entry.is_correct_location() == False
#     assert good_entry.is_valid_link() == False
#     assert good_entry.entry_complete() == False
#     assert good_entry.lock_entry() == None

# def test_prior_to_fix_locations(good_entry):
#     assert os.path.islink(good_entry.src) == False
#     assert os.path.isfile(good_entry.dst) == False

# @pytest.fixture
# def good_entry_fixed(good_entry):
#     good_entry.fix()
#     return good_entry

# def test_good_entry_fixed(good_entry_fixed, temp_dir):
#     good_entry_tests(good_entry_fixed, temp_dir, '.bashrc')

# def test_good_entry_fixed_getters(good_entry_fixed):
#     hash_val = get_md5({ 'name': '.bashrc', 'src': good_entry_fixed.src, 'dst': good_entry_fixed.dst, 'linked': True })

#     assert good_entry_fixed.is_correct_location() == True
#     assert good_entry_fixed.is_valid_link() == True
#     assert good_entry_fixed.entry_complete() == True
#     assert good_entry_fixed.lock_entry() == dict(name='.bashrc', src=good_entry_fixed.src, dst=good_entry_fixed.dst, notes='', linked=True, hash=hash_val)

# def test_good_entry_fixed_locations(good_entry_fixed):
#     assert os.path.islink(good_entry_fixed.src)
#     assert os.path.isfile(good_entry_fixed.dst)
#     assert os.readlink(good_entry_fixed.src) == good_entry_fixed.dst


# @pytest.fixture
# def bad_entry():
#     from doty.classes.DotyEntry import DotyEntry
#     return DotyEntry({ 'name': 'bad_entry', 'linked': True })

# def bad_entry_tests(bad_entry, temp_dir):
#     src = str(temp_dir / 'bad_entry')
#     dst = str(temp_dir / 'dotfiles' / 'bad_entry')
#     hash = get_md5({ 'name': 'bad_entry', 'src': src, 'dst': dst, 'linked': False })
    
#     assert bad_entry.name == 'bad_entry'
#     assert bad_entry.src == src
#     assert bad_entry.dst == dst
#     assert bad_entry.notes == ''
#     assert bad_entry.linked == False
#     assert bad_entry.hash == hash
#     assert bad_entry.is_broken_entry() == True
#     assert bad_entry.vals() == dict(name='bad_entry', src=src, dst=dst, notes='', linked=False)
#     assert bad_entry.is_locked_entry() == False

# def test_bad_entry(bad_entry, temp_dir):
#     bad_entry_tests(bad_entry, temp_dir)

# def bad_getters(bad_entry):
#     assert bad_entry.is_correct_location() == False
#     assert bad_entry.is_valid_link() == False
#     assert bad_entry.entry_complete() == False
#     assert bad_entry.lock_entry() == None

# def test_bad_prior_to_fix_getters(bad_entry):
#     bad_getters(bad_entry)

# def bad_locations(bad_entry):
#     assert os.path.islink(bad_entry.src) == False
#     assert os.path.isfile(bad_entry.dst) == False

# def test_bad_prior_to_fix_locations(bad_entry):
#     bad_locations(bad_entry)

# @pytest.fixture
# def bad_entry_fixed(bad_entry):
#     bad_entry.fix()
#     return bad_entry

# def test_bad_entry_fixed(bad_entry_fixed, temp_dir):
#     bad_entry_tests(bad_entry_fixed, temp_dir)

# def test_bad_entry_fixed_getters(bad_entry_fixed):
#     bad_getters(bad_entry_fixed)

# def test_bad_entry_fixed_locations(bad_entry_fixed):
#     bad_locations(bad_entry_fixed)


# def test_undo(good_entry_fixed):
#     assert good_entry_fixed.entry_complete() == True

#     good_entry_fixed._locked_entry = True
#     assert good_entry_fixed.undo() == True
#     good_entry_fixed.run_checks()

#     assert good_entry_fixed.entry_complete() == False
#     assert good_entry_fixed.is_correct_location() == False
#     assert good_entry_fixed.is_valid_link() == False
#     assert good_entry_fixed.lock_entry() == None

#     assert not os.path.islink(good_entry_fixed.src)
#     assert not os.path.isfile(good_entry_fixed.dst)
#     assert os.path.isfile(good_entry_fixed.src)