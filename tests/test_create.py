import os
import logging
import yaml
import pytest

@pytest.fixture(scope='module')
def setup(temp_dir):
    from doty.classes.DotyEntries import DotyEntries
    cfg = temp_dir / 'dotfiles' / 'dotycfg.yml'
    lock = temp_dir / 'dotfiles' / 'doty_lock.yml'

    doty_entries = DotyEntries(['.bashrc', '.zshrc', '.zsh_history'])
    doty_entries.fix_all()

    with open(cfg, 'w') as f:
        yaml.safe_dump(doty_entries.get_cfg_entries(), f)
    
    with open(lock, 'w') as f:
        yaml.safe_dump(doty_entries.get_hashable_entries(), f)
    
    logger = logging.getLogger('doty')
    logger.setLevel(logging.ERROR)
    handler = logging.StreamHandler()
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)

@pytest.fixture
def create():
    from doty.create import main
    return main

def test_empty_files(temp_dir, create):
    with pytest.raises(SystemExit) as e:
        create(False, False)
    
    assert e.type == SystemExit
    assert e.value.code == 1

def test_stop_on_user_exit(setup, monkeypatch, create):
    monkeypatch.setattr('builtins.input', lambda _: 'EXIT')
    
    with pytest.raises(SystemExit) as e:
        create(False, False)
    
    assert e.type == SystemExit
    assert e.value.code == 0

def test_name_already_exists(setup, monkeypatch, create):
    monkeypatch.setattr('builtins.input', lambda _: '.bashrc')
    
    with pytest.raises(SystemExit) as e:
        create(False, False)
    
    assert e.type == SystemExit
    assert e.value.code == 1

def test_create_new_entry(setup, temp_dir, monkeypatch, create):
    (temp_dir / '.good_entry1').touch()
    inp = iter(['.good_entry1', '', '', '', '', '', ''])
    monkeypatch.setattr('builtins.input', lambda _: next(inp))

    create(False, False)

    lock_path = temp_dir / 'dotfiles' / 'doty_lock.yml'
    home_path = temp_dir / '.good_entry1'
    dotfiles_path = temp_dir / 'dotfiles' / '.good_entry1'
    with open(lock_path) as f:
        lock_yml = yaml.safe_load(f)
    
    assert '.good_entry1' in [ e['name'] for e in lock_yml ]
    assert os.path.islink(home_path)
    assert os.path.isfile(dotfiles_path)

def test_create_new_unlinked_entry(setup, temp_dir, monkeypatch, create):
    (temp_dir / '.good_entry2').touch()
    inp = iter(['.good_entry2', '', '', '', 'n', ''])
    monkeypatch.setattr('builtins.input', lambda _: next(inp))

    create(False, False)

    lock_path = temp_dir / 'dotfiles' / 'doty_lock.yml'
    home_path = temp_dir / '.good_entry2'
    dotfiles_path = temp_dir / 'dotfiles' / '.good_entry2'
    with open(lock_path) as f:
        lock_yml = yaml.safe_load(f)
    
    assert '.good_entry2' in [ e['name'] for e in lock_yml ]
    assert not os.path.islink(home_path)
    assert os.path.isfile(dotfiles_path)

# NOTE: This test needs to have the -s flag to work
def test_create_errors(setup, temp_dir, monkeypatch, create, capfd):
    (temp_dir / '.good_entry3').touch()
    inp = iter(['','.good_entry3', '', '', '', 'n', ''])
    monkeypatch.setattr('builtins.input', lambda _: next(inp))

    create(False, False)
    capture = capfd.readouterr()
    assert capture.err == '\033[1;31mName cannot be empty\n\n'
    
        


    