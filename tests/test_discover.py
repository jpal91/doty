import os
import pytest
import yaml
from doty.discover import find_all_dotfiles, get_new_entries, gen_temp_lock_file, discover
from doty.classes.entry import DotyEntry

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({'HOME': str(temp_dir)})

    yield

    with open(temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml', 'w') as f:
        f.write('')

def test_find_all_dotfiles(temp_dir):
    dotfiles = find_all_dotfiles()
    dot_dir = temp_dir / 'dotfiles'

    assert len(dotfiles) == 5
    assert str(dot_dir / '.dot_file1') in dotfiles
    assert str(dot_dir / '.dot_file2') in dotfiles
    assert str(dot_dir / 'dot_dir' / '.dot_file3') in dotfiles
    assert str(dot_dir / 'dot_dir' / 'dot_file4') in dotfiles
    assert str(dot_dir / '.dot_file5') not in dotfiles
    assert str(dot_dir / '.gitignore') not in dotfiles
    assert all([not df.startswith(str(dot_dir / '.doty_config')) for df in dotfiles])

@pytest.fixture
def dummy_lock_file(temp_dir):
    # doty_lock = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'
    entries = [DotyEntry(e).dict for e in [
        {'name': '.dot_file1'},
        {'name': '.dot_file2'},
        {'name': '.dot_file3', 'dst': str(temp_dir / 'dotfiles' / 'dot_dir' / '.dot_file3')},
    ]]
    # with open(doty_lock, 'w') as f:
    #     yaml.dump(entries, f)
    return entries


def test_get_new_entries(temp_dir, dummy_lock_file):
    pass