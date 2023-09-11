import os
import pytest
import yaml
from doty.discover import find_all_dotfiles, get_new_entries, gen_temp_lock_file, discover
from doty.classes.entry import DotyEntry
from doty.helpers.git import last_commit_file

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles"), 'GIT_AUTO_COMMIT': 'false' })

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
    (temp_dir / 'dotfiles' / '.dot_file7').touch()
    (temp_dir / 'dotfiles' / 'test').mkdir()
    (temp_dir / 'dotfiles' / 'test' / '.dot_file8').touch()
    (temp_dir / 'dotfiles' / 'test' / '.dot_file1').touch() # Has same basename as an existing file so should be skipped
    entries = [DotyEntry(e).dict for e in [
        {'name': '.dot_file1'},
        {'name': '.dot_file2'},
        {'name': '.dot_file3', 'dst': str(temp_dir / 'dotfiles' / 'dot_dir' / '.dot_file3')},
        {'name': 'dot_file4', 'dst': str(temp_dir / 'dotfiles' / 'dot_dir' / 'dot_file4')},
        {'name': '.dot_file6', 'dst': str(temp_dir / 'dotfiles' / 'dot_dir' / '.dot_file6')},
    ]]
    # with open(doty_lock, 'w') as f:
    #     yaml.dump(entries, f)
    yield entries
    (temp_dir / 'dotfiles' / '.dot_file7').unlink()
    (temp_dir / 'dotfiles' / 'test' / '.dot_file8').unlink()
    (temp_dir / 'dotfiles' / 'test' / '.dot_file1').unlink() # Has same basename as an existing file so should be skipped
    (temp_dir / 'dotfiles' / 'test').rmdir()


def test_get_new_entries(temp_dir, dummy_lock_file):
    expected = [
        DotyEntry({'name': '.dot_file7'}).dict, 
        DotyEntry({'name': '.dot_file8', 'dst': str(temp_dir / 'dotfiles' / 'test' / '.dot_file8')}).dict
    ]
    dotfiles = find_all_dotfiles()
    lock_entries = dummy_lock_file

    new_entries = get_new_entries(dotfiles, lock_entries)
    assert len(new_entries) == 2
    assert new_entries == expected

def test_gen_temp_lock_file(temp_dir, dummy_lock_file):
    doty_lock = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'
    with open(doty_lock, 'w') as f:
        yaml.safe_dump(dummy_lock_file, f, sort_keys=False)
    
    temp_lock_file = gen_temp_lock_file(dummy_lock_file + [DotyEntry({'name': '.dot_file7'}).dict])
    assert os.path.isfile(temp_lock_file)
    assert temp_lock_file == str(temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock_tmp.yml')

    with open(temp_lock_file, 'r') as f:
        entries = yaml.safe_load(f)
        assert len(entries) == 6
        assert entries != dummy_lock_file
        assert entries[-1]['name'] == '.dot_file7'

def test_discover(temp_dir, git_repo, dummy_lock_file):
    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'
    temp_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock_tmp.yml'
    last_commit = yaml.safe_load(last_commit_file(".doty_config/doty_lock.yml"))
    expected = [
        DotyEntry({'name': '.dot_file7'}).dict, 
        DotyEntry({'name': '.dot_file8', 'dst': str(temp_dir / 'dotfiles' / 'test' / '.dot_file8')}).dict
    ]
    assert len(last_commit) == 5
    discover()

    with open(doty_lock_path) as f:
        current_lock = yaml.safe_load(f)
    
    assert current_lock == last_commit

    with open(temp_lock_path) as f:
        temp_lock = yaml.safe_load(f)
    
    assert temp_lock == [*last_commit, *expected]