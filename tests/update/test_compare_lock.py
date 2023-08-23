import os
import shutil
import pytest
import yaml

@pytest.fixture(scope='module')
def setup(temp_dir):
    from doty.classes.DotyEntries import DotyEntries
    from doty.update import compare_lock
    examples = os.path.realpath(os.path.join(__file__, '..', '..', '..', 'examples'))
    cfg_path = os.path.join(examples, 'dotycfg.yml')
    lock_path = os.path.join(examples, 'doty_lock.yml')
    tmp_cfg_path = temp_dir / 'dotfiles' / '.doty_config' / 'dotycfg.yml'
    tmp_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'

    with open(cfg_path) as f:
        cfg_yml = yaml.safe_load(f)
    
    with open(lock_path) as f:
        lock_yml = yaml.safe_load(f)
    
    shutil.copy(cfg_path, tmp_cfg_path)
    shutil.copy(lock_path, tmp_lock_path)

    DotyEntries(lock_yml).fix_all()
    
    yield cfg_yml, lock_yml, compare_lock

    with open(tmp_lock_path) as f:
        f.write('')
    
    with open(tmp_cfg_path) as f:
        f.write('')

# @pytest.fixture(scope='module')
# def doty_entries():
#     from doty.classes.DotyEntries import DotyEntries
#     return DotyEntries

def get_entries(cfg_yml, lock_yml):
    from doty.classes.DotyEntries import DotyEntries
    return DotyEntries(cfg_yml), DotyEntries(lock_yml)

def test_no_changes(setup, capfd):
    cfg_yml, lock_yml, compare_lock = setup
    cfg, lock = get_entries(cfg_yml, lock_yml)
    add, remove, update = compare_lock(cfg, lock)
    
    assert add == []
    assert remove == []
    assert update == []

