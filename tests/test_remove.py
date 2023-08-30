import os
import pytest
from doty.remove import remove, remove_link, remove_file

@pytest.fixture(scope="module", autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles")})
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

def test_remove(temp_dir, monkeypatch):
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