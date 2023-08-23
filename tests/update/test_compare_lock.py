import os
import pytest
import yaml

@pytest.fixture(scope='module')
def setup():
    from doty.classes.DotyEntries import DotyEntries
    from doty.update import compare_lock

    entries = DotyEntries(['.bashrc', '.zshrc', '.zsh_history'])
    entries.fix_all()

    cfg_yml = entries.get_cfg_entries()
    lock_yml = entries.get_hashable_entries()

    yield cfg_yml, lock_yml, compare_lock

    for e in entries.entries:
        if not e.entry_complete():
            continue
        e._locked_entry = True
        e.undo()



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
    assert remove == []
    assert update == []

