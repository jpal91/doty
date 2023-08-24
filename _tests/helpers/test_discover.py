import os
import pytest
from _doty.helpers.discover import find_all_dotfiles, find_all_links, get_doty_ignore, discover

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir):
    dotfiles = temp_dir / 'dotfiles'
    (dotfiles / '.dot_file1').touch()
    (dotfiles / '.dot_file2').touch()
    (dotfiles / 'dot_dir').mkdir()
    (dotfiles / 'dot_dir' / '.dot_file3').touch()
    (dotfiles / 'dot_dir' / 'dot_file4').touch()
    (dotfiles / 'dot_dir' / '.dot_file6').touch()
    (temp_dir / '.dot_file1').symlink_to(dotfiles / '.dot_file1')
    (temp_dir / '.dot_file2').symlink_to(dotfiles / '.dot_file2')
    (temp_dir / '.dot_file3').symlink_to(dotfiles / 'dot_dir' / '.dot_file3')
    (temp_dir / '.dot_file5').touch()
    os.environ.update({'HOME': str(temp_dir)})

def test_get_doty_ignore(temp_dir):
    doty_ignore = get_doty_ignore()
    di_path = temp_dir / 'dotfiles' / '.dotyignore'

    assert len(doty_ignore) == 0

    with open(di_path, 'w') as di:
        di.write('.dot_file6')

    doty_ignore = get_doty_ignore()

    assert len(doty_ignore) == 1
    assert doty_ignore[0] == '.dot_file6'

def test_find_all_dotfiles(temp_dir):
    dotfiles = find_all_dotfiles(['.dot_file6'])
    dot_dir = temp_dir / 'dotfiles'

    assert len(dotfiles) == 4
    assert str(dot_dir / '.dot_file1') in dotfiles
    assert str(dot_dir / '.dot_file2') in dotfiles
    assert str(dot_dir / 'dot_dir' / '.dot_file3') in dotfiles
    assert str(dot_dir / 'dot_dir' / 'dot_file4') in dotfiles
    assert str(dot_dir / '.dot_file5') not in dotfiles
    assert str(dot_dir / 'dot_dir' / '.dot_file6') not in dotfiles

def test_find_all_links(temp_dir):
    dotfiles = find_all_dotfiles(['.dot_file6'])
    links = find_all_links(dotfiles)

    assert len(links) == 3
    assert str(temp_dir / '.dot_file1') in links
    assert str(temp_dir / '.dot_file2') in links
    assert str(temp_dir / '.dot_file3') in links
    assert str(temp_dir / '.dot_file4') not in links
    assert str(temp_dir / '.dot_file5') not in links
    assert str(temp_dir / '.dot_file6') not in links

def test_discover(temp_dir):
    links = discover()

    assert len(links) == 1
    assert str(temp_dir / 'dotfiles' / 'dot_dir' / 'dot_file4') in links
    assert str(temp_dir / 'dotfiles' / 'dot_dir' / '.dot_file6') not in links
