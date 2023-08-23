import os
import pytest
import yaml

@pytest.fixture(scope='module')
def setup_init():
    from doty.classes.DotyEntries import DotyEntries

    entries = DotyEntries(['.bashrc', '.zshrc', '.zsh_history'])
    entries.fix_all()

    yield entries

    for e in entries.entries:
        if not e.entry_complete():
            continue
        e._locked_entry = True
        e.undo()

@pytest.fixture
def setup(setup_init):
    from doty.update import compare_lock
    entries = setup_init

    cfg_yml = entries.get_cfg_entries()
    lock_yml = entries.get_hashable_entries()

    yield cfg_yml, lock_yml, compare_lock


def get_entries(cfg_yml, lock_yml):
    from doty.classes.DotyEntries import DotyEntries
    return DotyEntries(cfg_yml), DotyEntries(lock_yml)

def test_no_changes(setup):
    cfg_yml, lock_yml, compare_lock = setup
    cfg, lock = get_entries(cfg_yml, lock_yml)
    add, remove, update = compare_lock(cfg, lock)

    assert add == []
    assert remove == []
    assert update == []

def test_add(setup):
    cfg_yml, lock_yml, compare_lock = setup
    cfg_yml.append('.lesshst')
    
    cfg, lock = get_entries(cfg_yml, lock_yml)
    add, remove, update = compare_lock(cfg, lock)

    assert add == [cfg.entries[-1]]
    assert len(add) == 1
    assert remove == []
    assert update == []


def test_update(setup):
    cfg_yml, lock_yml, compare_lock = setup
    cfg_yml[0]['linked'] = not cfg_yml[0]['linked']

    cfg, lock = get_entries(cfg_yml, lock_yml)
    add, remove, update = compare_lock(cfg, lock)

    assert add == []
    assert remove == []
    assert len(update) == 1

    assert update[0][0].name == cfg_yml[0]['name']
    assert update[0][0].linked == (not cfg_yml[0]['linked'])


def test_remove(setup):
    cfg_yml, lock_yml, compare_lock = setup
    removed = cfg_yml.pop()

    cfg, lock = get_entries(cfg_yml, lock_yml)
    add, remove, update = compare_lock(cfg, lock)

    assert add == []
    assert update == []
    assert len(remove) == 1

    removed_entry = remove[0]

    assert removed_entry.name == removed['name']



