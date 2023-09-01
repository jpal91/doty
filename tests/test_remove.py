import os
from pathlib import Path
import pytest
from doty.remove import remove, remove_link, remove_file
from doty.update import update
from doty.classes.entry import DotyEntry
from doty.helpers.utils import write_lock_file

@pytest.fixture(scope="module", autouse=True)
def setup(temp_dir, dummy_files, git_repo):
    os.environ.update({"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles"), 'GIT_AUTO_COMMIT': 'false'})
    (temp_dir / 'dotfiles' / '.doty_lfile1').touch()
    (temp_dir / 'dotfiles' / '.doty_lfile2').touch()
    (temp_dir / 'dotfiles' / 'dot_dir' / '.doty_lfile3').touch()
    os.symlink(temp_dir / "dotfiles" / ".doty_lfile1", temp_dir / ".doty_lfile1")
    os.symlink(temp_dir / "dotfiles" / ".doty_lfile2", temp_dir / ".doty_lfile2")
    os.symlink(temp_dir / "dotfiles" / 'dot_dir' / ".doty_lfile3", temp_dir / ".doty_lfile3")

# @pytest.fixture(scope='module')
# def temp_links(temp_dir, setup):
#     (temp_dir / 'dotfiles' / '.doty_lfile1').touch()
#     (temp_dir / 'dotfiles' / '.doty_lfile2').touch()
#     (temp_dir / 'dotfiles' / 'dot_dir' / '.doty_lfile3').touch()
#     os.symlink(temp_dir / "dotfiles" / ".doty_lfile1", temp_dir / ".doty_lfile1")
#     os.symlink(temp_dir / "dotfiles" / ".doty_lfile2", temp_dir / ".doty_lfile2")
#     os.symlink(temp_dir / "dotfiles" / 'dot_dir' / ".doty_lfile3", temp_dir / ".doty_lfile3")

@pytest.mark.parametrize(
    'input,error',
    [
        ('.doty_lfile1', False),
        ('.doty_lfile2', False),
        ('.doty_lfile3', False),
        ('.good_entry1', True),
        ('.good_entry2', True)
    ]
)
def test_remove_link(temp_dir, input, error):
    path = temp_dir / input

    if error:
        with pytest.raises(SystemExit) as exit:
            remove_link(path)
        
        assert exit.type == SystemExit
        assert exit.value.code == 1
    else:
        assert os.path.islink(path)
        remove_link(path)
        assert not os.path.islink(path)

@pytest.mark.parametrize(
    'input,error',
    [
        ('.doty_lfile1', False),
        ('.doty_lfile2', False),
        ('dot_dir/.doty_lfile3', False),
        ('.good_entry1', True),
        ('.good_entry2', True)
    ]
)
def test_remove_file(temp_dir, input, error):
    path = temp_dir / 'dotfiles' / input

    if error:
        with pytest.raises(SystemExit) as exit:
            remove_file(path)
        
        assert exit.type == SystemExit
        assert exit.value.code == 1
    else:
        assert os.path.isfile(path)
        remove_file(path)
        assert not os.path.isfile(path)
        assert os.path.isfile(temp_dir / os.path.basename(input))

def _test_remove(temp_dir, monkeypatch):
    monkeypatch.setattr('doty.remove.update', lambda *args, **kwargs: None)

    with pytest.raises(SystemExit) as exit:
        remove('no_exist')
    
    assert exit.type == SystemExit
    assert exit.value.code == 1

    monkeypatch.setattr('builtins.input', lambda _: 'n')

    with pytest.raises(SystemExit) as exit:
        remove('.dot_file1', force=False)
    
    assert exit.type == SystemExit
    assert exit.value.code == 0

    (temp_dir / 'dotfiles' / '.doty_lfile4').touch()
    # os.symlink(temp_dir / "dotfiles" / ".doty_lfile4", temp_dir / ".doty_lfile4")
    monkeypatch.setattr('doty.remove.remove_link', lambda *_: None)

    with pytest.raises(SystemExit) as exit:
        remove('.doty_lfile4', link_only=True)
    
    assert exit.type == SystemExit
    assert exit.value.code == 0

def test_remove(temp_dir: Path, monkeypatch):
    files = [
        (temp_dir / '.doty_rm1'),
        (temp_dir / '.doty_rm2'),
        (temp_dir / '.doty_rm3'),
        (temp_dir / '.doty_rm4')
    ]
    [file.touch() for file in files]
    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'

    entries = [DotyEntry({ 'name': os.path.basename(file) }) for file in files]
    entries[1].dst = str(temp_dir / 'dotfiles' / 'nest1' / '.doty_rm2')
    entries[2].linked = False
    write_lock_file([e.dict for e in entries], doty_lock_path)
    update(quiet=True)

    # Test exit code 3 == no entry found
    with pytest.raises(SystemExit) as exit:
        remove('no_exist')
    
    assert exit.type == SystemExit
    assert exit.value.code == 3

    # Test exit code 4 == user did not confirm
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    with pytest.raises(SystemExit) as exit:
        remove('.doty_rm1', force=False)
    
    assert exit.type == SystemExit
    assert exit.value.code == 4

    # Test normal functionality
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    remove('.doty_rm1')
    assert not os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm1')
    assert not os.path.islink(temp_dir / '.doty_rm1')
    assert os.path.isfile(temp_dir / '.doty_rm1')

    monkeypatch.setattr('builtins.input', lambda _: 'y')
    remove('.doty_rm2')
    assert not os.path.isfile(temp_dir / 'dotfiles' / 'nest1' / '.doty_rm2')
    assert not os.path.islink(temp_dir / '.doty_rm2')
    assert os.path.isfile(temp_dir / '.doty_rm2')
    assert not os.path.isdir(temp_dir / 'dotfiles' / 'nest1')

    remove('.doty_rm3', force=True)
    assert not os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm3')
    assert not os.path.islink(temp_dir / '.doty_rm3')
    assert os.path.isfile(temp_dir / '.doty_rm3')

    assert os.path.islink(temp_dir / '.doty_rm4')
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    remove('.doty_rm4', link_only=True)
    assert os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm4')
    assert not os.path.islink(temp_dir / '.doty_rm4')