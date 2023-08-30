import os
import pytest
from doty.helpers.discover import find_all_dotfiles, find_all_links, get_doty_ignore, discover

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({'HOME': str(temp_dir)})

def test_get_doty_ignore(temp_dir):
    doty_ignore = get_doty_ignore()
    di_path = temp_dir / 'dotfiles' / '.doty_config' / '.dotyignore'

    assert len(doty_ignore) == 0

    with open(di_path, 'w') as di:
        di.write('.dot_file6')

    doty_ignore = get_doty_ignore()

    assert len(doty_ignore) == 1
    assert doty_ignore[0] == '.dot_file6'

    with open(di_path, 'a') as di:
        di.write('\n# This is a test of a comment')
    
    doty_ignore = get_doty_ignore()

    assert len(doty_ignore) == 1
    assert doty_ignore[0] == '.dot_file6'
    assert '# This is a test of a comment' not in doty_ignore

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

def test_find_all_links(temp_dir):
    dotfiles = find_all_dotfiles()
    links = find_all_links(dotfiles)

    assert len(links) == 3
    assert str(temp_dir / '.dot_file1') in links
    assert str(temp_dir / '.dot_file2') in links
    assert str(temp_dir / '.dot_file3') in links
    assert str(temp_dir / '.dot_file4') not in links
    assert str(temp_dir / '.dot_file5') not in links
    assert str(temp_dir / '.dot_file6') not in links

def test_discover(temp_dir):
    links, unlinks = discover()

    assert len(links) == 1
    assert str(temp_dir / 'dotfiles' / 'dot_dir' / 'dot_file4') in links
    assert str(temp_dir / 'dotfiles' / 'dot_dir' / '.dot_file6') not in links
    assert len(unlinks) == 0

    di_path = temp_dir / 'dotfiles' / '.doty_config' / '.dotyignore'

    with open(di_path, 'a') as f:
        f.write('\n.dot_file2')
    
    links, unlinks = discover()

    assert len(unlinks) == 1
    assert len(links) == 1
    assert '.dot_file2' in unlinks
