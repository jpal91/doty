import os
from pathlib import Path
import signal
import pytest
from doty.add import get_user_input, double_check, get_name, get_dst, get_src, add

@pytest.fixture(scope="module", autouse=True)
def setup(temp_dir, dummy_files, git_repo):
    os.environ.update({"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles"), 'GIT_AUTO_COMMIT': 'false' })
    yield
    with open(temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml', 'w') as f:
        f.write('')


@pytest.mark.parametrize("input", ["test", "test2", "test3", ""])
def test_get_user_input(input, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: input)
    user_input = get_user_input("test")
    assert user_input == input


def test_exit_on_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "EXIT")
    with pytest.raises(SystemExit) as exit:
        get_user_input("test")

    assert exit.type == SystemExit
    assert exit.value.code == 0

def test_keyboard_interrupt_on_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: signal.raise_signal(signal.SIGINT))
    with pytest.raises(SystemExit) as exit:
        get_user_input("test")

    assert exit.type == SystemExit
    assert exit.value.code == 0

@pytest.mark.parametrize('input,expected', [('y', True), ('n', False), ('', True), ('k', False), ('Y', True)])
def test_check(input, expected, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: input)
    user_input = double_check("test", "test")
    assert user_input == expected

def test_exit_on_check(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "EXIT")
    with pytest.raises(SystemExit) as exit:
        double_check("test", "test")

    assert exit.type == SystemExit
    assert exit.value.code == 0

def test_keyboard_interrupt_on_check(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: signal.raise_signal(signal.SIGINT))
    with pytest.raises(SystemExit) as exit:
        double_check("test", "test")

    assert exit.type == SystemExit
    assert exit.value.code == 0

def test_get_name(monkeypatch, capfd):
    inputs = iter(["", "test"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    name = get_name()
    err = capfd.readouterr().err
    assert name == "test"
    assert err == "\033[1;31mName cannot be empty, please try again.\033[0m\n"

def test_get_src(temp_dir: Path, monkeypatch):
    name = 'test'

    monkeypatch.setattr('builtins.input', lambda _: '')
    src = get_src(name)
    assert src == str(temp_dir / name)

    monkeypatch.setattr('builtins.input', lambda _: str(temp_dir / 'config/test'))
    src = get_src(name)
    assert src == str(temp_dir / 'config/test')

    monkeypatch.setattr('builtins.input', lambda _: '~/test1')
    src = get_src(name)
    assert src == str(temp_dir / 'test1')

def test_get_dst(temp_dir: Path, monkeypatch):
    name = 'test'

    monkeypatch.setattr('builtins.input', lambda _: '')
    src = get_dst(name)
    assert src == str(temp_dir / 'dotfiles' / name)

    monkeypatch.setattr('builtins.input', lambda _: 'config/test')
    src = get_dst(name)
    assert src == str(temp_dir / 'dotfiles' / 'config/test')

    monkeypatch.setattr('builtins.input', lambda _: 'test1')
    src = get_dst(name)
    assert src == str(temp_dir / 'dotfiles' / 'test1')

@pytest.mark.parametrize(
    'keyargs,expected',
    [
        ({ 'entry_name': '.good_entry1', 'src': '.good_entry1', 'dst': 'dotfiles/.good_entry1', 'link_name': '.good_entry1' }, 'COMPLETE'),
        ({ 'entry_name': '.good_entry1', 'src': '~/.good_entry1', 'dst': 'dotfiles/.good_entry1', 'link_name': '.good_entry1', 'force': True }, 'COMPLETE'),
        ({ 'entry_name': '.good_entry1', 'src': '', 'dst': '~/dotfiles/.good_entry1', 'link_name': '', 'no_link': False }, 'COMPLETE'),
        ({ 'entry_name': '', 'src': '.good_entry1', 'dst': 'dotfiles/.good_entry1', 'link_name': '', 'no_link': True }, 'COMPLETE'),
        ({ 'entry_name': '.good_entry1', 'src': 'nest1/nest2/../../.good_entry1', 'dst': 'dotfiles/nest1/nest2/../../.good_entry1', 'link_name': '.good_entry1', }, 'COMPLETE'),
        ({ 'entry_name': '', 'src': '', 'dst': '','link_name': '', 'no_link': False }, 'COMPLETE'),
        ({ 'entry_name': '.good_entry1', 'src': '/usr/bin/bash', 'dst': 'dotfiles/.good_entry1', 'link_name': '.good_entry1', }, 'NO_HOME'),
        ({ 'entry_name': '.good_entry1', 'src': '/usr/bin/zshrc', 'dst': 'dotfiles/.good_entry1', 'link_name': '.good_entry1', }, 'NO_HOME'),
        ({ 'entry_name': '.good_entry1', 'src': '.good_entry1', 'dst': 'dotfiles/.good_entry1', 'link_name': '.good_entry1' }, 'NO_CONFIRM'),
        ({ 'entry_name': '.good_entry1', 'src': '.entry_no_exist', 'dst': 'dotfiles/.good_entry1', 'link_name': '.good_entry1', 'force': True }, 'BAD_SRC'),
        ({ 'entry_name': '.good_entry1', 'src': '.good_entry1', 'dst': '~/.config/.good_entry1', 'link_name': '.good_entry1', 'force': True }, 'BAD_DST'),
    ]
)
def test_add(temp_dir, monkeypatch, keyargs, expected, capfd):
    os.chdir(temp_dir)

    # Tests multiple kwargs to add which will result in a entry being succesfully added
    if expected == 'COMPLETE':
        monkeypatch.setattr('doty.add.update', lambda **_: None)
        monkeypatch.setattr('doty.add.add_to_lock_file', lambda *_: None)
        monkeypatch.setattr('doty.add.double_check', lambda *_: True)
        name, src, dst, link_name = '.good_entry1', str(temp_dir / '.good_entry1'), str(temp_dir / 'dotfiles' / '.good_entry1'), '.good_entry1'
        linked = not keyargs['no_link'] if 'no_link' in keyargs else True

        if not keyargs['entry_name']:
            monkeypatch.setattr('doty.add.get_name', lambda: name)
        
        if not keyargs['src']:
            monkeypatch.setattr('doty.add.get_src', lambda *_: src)
        
        if not keyargs['dst']:
            monkeypatch.setattr('doty.add.get_dst', lambda *_: dst)
        
        if not keyargs['link_name']:
            monkeypatch.setattr('doty.add.get_link_name', lambda *_: link_name)
        
        res = add(**keyargs)

        assert res['name'] == name
        assert res['src'] == src
        assert res['dst'] == dst
        assert res['linked'] == linked
        assert res['link_name'] == link_name
    
    # Tests if the user input a src that is not in the home directory which will ask for confirmation
    elif expected == 'NO_HOME':
        monkeypatch.setattr('doty.add.update', lambda **_: None)
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        with pytest.raises(SystemExit) as exit:
            add(**keyargs)
        
        assert exit.type == SystemExit
        assert exit.value.code == 3
        assert not os.path.exists(temp_dir / 'dotfiles' / '.good_entry1')
    
    # Tests whether the user declines confirmation
    elif expected == 'NO_CONFIRM':
        monkeypatch.setattr('doty.add.update', lambda **_: None)
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        with pytest.raises(SystemExit) as exit:
            add(**keyargs)
        
        assert exit.type == SystemExit
        assert exit.value.code == 4
        assert not os.path.exists(temp_dir / 'dotfiles' / '.good_entry1')
    
    # Tests that error is thrown with a bad src path
    elif expected == 'BAD_SRC':
        add(**keyargs)
        err = capfd.readouterr().err
        assert 'Error' in err
        assert 'does not exist' in err
        assert not os.path.exists(temp_dir / 'dotfiles' / '.good_entry1')
    
    # Tests that error is thrown with a bad dst path
    elif expected == 'BAD_DST':
        add(**keyargs)
        err = capfd.readouterr().err
        assert 'Error' in err
        assert 'not in the dotfiles directory' in err
        assert not os.path.exists(temp_dir / 'dotfiles' / '.good_entry1')