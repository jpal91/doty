import os
from pathlib import Path
import pytest
from doty.remove import remove, remove_link, remove_file, remove_multi
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
    yield

    with open(temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml', 'w') as f:
        f.write('')

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
        (temp_dir / '.doty_rm4'),
        (temp_dir / '.doty_rm5')
    ]
    [file.touch() for file in files]
    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'

    entries = [DotyEntry({ 'name': os.path.basename(file) }) for file in files]
    entries[1].dst = str(temp_dir / 'dotfiles' / 'nest1' / '.doty_rm2')
    entries[2].linked = False
    entries[4].link_name = '.doty_rm5_unique'
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

    # Correctly removes nested entry + empty dirs
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    remove('.doty_rm2')
    assert not os.path.isfile(temp_dir / 'dotfiles' / 'nest1' / '.doty_rm2')
    assert not os.path.islink(temp_dir / '.doty_rm2')
    assert os.path.isfile(temp_dir / '.doty_rm2')
    assert not os.path.isdir(temp_dir / 'dotfiles' / 'nest1')

    # Correctly removes non-linked entry and doesn't confirm
    remove('.doty_rm3', force=True)
    assert not os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm3')
    assert not os.path.islink(temp_dir / '.doty_rm3')
    assert os.path.isfile(temp_dir / '.doty_rm3')

    # Correctly removes only the link but keeps file
    assert os.path.islink(temp_dir / '.doty_rm4')
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    remove('.doty_rm4', link_only=True)
    assert os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm4')
    assert not os.path.islink(temp_dir / '.doty_rm4')

    # Correctly removes file that has a unique link name different from entry name
    assert os.path.islink(temp_dir / '.doty_rm5_unique')
    assert os.path.exists(temp_dir / 'dotfiles' / '.doty_rm5')
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    remove('.doty_rm5_unique')
    assert not os.path.islink(temp_dir / '.doty_rm5_unique')
    assert not os.path.exists(temp_dir / 'dotfiles' / '.doty_rm5')
    assert os.path.isfile(temp_dir / '.doty_rm5')

def test_remove_multi(temp_dir: Path, monkeypatch, capfd):
    files = [
        (temp_dir / '.doty_rm6'),
        (temp_dir / '.doty_rm7'),
        (temp_dir / '.doty_rm8'),
        (temp_dir / '.doty_rm9'),
        (temp_dir / '.doty_rm10')
    ]
    [file.touch() for file in files]
    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'

    entries = [DotyEntry({ 'name': os.path.basename(file) }) for file in files]
    # entries[1].dst = str(temp_dir / 'dotfiles' / 'nest1' / '.doty_rm2')
    # entries[2].linked = False
    # entries[4].link_name = '.doty_rm5_unique'
    write_lock_file([e.dict for e in entries], doty_lock_path)
    update(quiet=True)

    assert all([os.path.islink(file) for file in files])

    inp = iter(['y', 'y', 'n'])
    monkeypatch.setattr('builtins.input', lambda _: next(inp))
    remove_multi(['.doty_rm6', '.doty_rm7', '.doty_rm8'])
    out = capfd.readouterr().err
    assert 'Removing \x1b[1;37m.doty_rm6' in out
    assert 'Removing \x1b[1;37m.doty_rm7' in out
    assert 'Skipping .doty_rm8' in out
    assert not os.path.islink(temp_dir / '.doty_rm6')
    assert not os.path.islink(temp_dir / '.doty_rm7')
    assert os.path.isfile(temp_dir / '.doty_rm6')
    assert os.path.isfile(temp_dir / '.doty_rm7')
    assert os.path.islink(temp_dir / '.doty_rm8')
    assert not os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm6')
    assert not os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm7')
    assert os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm8')

    inp = iter(['y', 'y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inp))
    remove_multi(['.doty_rm8', '.doty_rm9'], link_only=True)
    out = capfd.readouterr().err
    assert 'Removing \x1b[1;37mlink for .doty_rm8' in out
    assert 'Removing \x1b[1;37mlink for .doty_rm9' in out
    assert not os.path.islink(temp_dir / '.doty_rm8')
    assert not os.path.islink(temp_dir / '.doty_rm9')
    assert os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm8')
    assert os.path.isfile(temp_dir / 'dotfiles' / '.doty_rm9')

    remove_multi(['.doty_rm10', 'no_exist'], force=True)
    out = capfd.readouterr().err
    assert not os.path.islink(temp_dir / '.doty_rm10')
    assert os.path.isfile(temp_dir / '.doty_rm10')
    assert 'Could not find dotfile no_exist' in out
    assert 'Removing \x1b[1;37m.doty_rm10' in out