import os
import pytest
import signal
from doty.add import get_user_input, double_check, get_name, get_src, find_src, get_dst, add_doty_ignore
from doty.classes.DotyLogger import DotyLogger


@pytest.fixture(scope="module", autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles")})
    logger = DotyLogger()


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
    name = get_name(check=False)
    err = capfd.readouterr().err
    assert name == "test"
    assert err == "\033[1;31mName cannot be empty, please try again.\033[0m\n"

@pytest.mark.parametrize(
    "input,error",
    [
        ("f", True),
        ("test", True),
        ("/tmp/dotytmp/dotfiles/.good_entry1", True),
        ('dotfiles/.dot_file1', False),
        (".good_entry2", False),
        (".good_entry3", False),
    ]
)
def test_find_src(temp_dir, input, error):
    home = temp_dir
    
    if error:
        src = find_src(input)
        assert src == ""
    else:
        src = find_src(input)
        assert src == str(home / input)
    

@pytest.mark.parametrize(
    "input,expected",
    [
        (
            ["", ".good_entry1"],
            "\033[1;31mSource path cannot be empty, please try again.\033[0m\n",
        ),
        ([".good_entry1"], ""),
        (
            ['.bad_entry1', '.good_entry1'],
            "\033[1;31mSource path does not exist, please try again.\033[0m\n",
        ),
        (
            ['dotfiles/.dot_file1', '.good_entry1'],
            "\033[1;31mSource path cannot be in dotfiles directory, please try again.\033[0m\n",
        )
    ],
)
def test_get_src(temp_dir, input, expected, monkeypatch, capfd):
    inputs = iter(input)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    name = get_src(check=False)
    err = capfd.readouterr().err
    assert name == str(temp_dir / ".good_entry1")
    assert err == expected

@pytest.mark.parametrize(
    "input,expected,error",
    [
        ('', '.good_entry1', ''),
        ('test', 'test', ''),
        ('dotfiles/.dot_file1', 'dotfiles/.dot_file1', ''),
        (['.dot_file1', '.dot_file1.alt'], '.dot_file1.alt', '\033[1;31mDestination path already exists, please try again.\033[0m\n'),
    ],
)
def test_get_dst(temp_dir, input, error, expected, monkeypatch, capfd):
    inputs = iter(input if isinstance(input, list) else [input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    name = get_dst('.good_entry1', check=False)
    err = capfd.readouterr().err
    assert name == str(temp_dir / 'dotfiles' / expected)
    # err = err.replace('\x1b[1;37mEnter the destination path of the dotfile (or leave blank for default .good_entry1):\x1b[0m\n', '')
    assert err ==  error

def test_add_doty_ignore(temp_dir):
    dotyignore_path = temp_dir / 'dotfiles' / '.doty_config' / '.dotyignore'

    with open(dotyignore_path, 'w') as f:
        f.write('')

    add_doty_ignore('.ignore_entry')

    with open(dotyignore_path, 'r') as f:
        current = f.readlines()
    
    assert current == ['.ignore_entry\n']