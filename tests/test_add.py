import os
from pathlib import Path
import signal
import pytest
from doty.add import get_user_input, double_check, get_name, get_dst, get_link_name, get_src

@pytest.fixture(scope="module", autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles"), 'GIT_AUTO_COMMIT': 'false' })


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

    monkeypatch.setattr('builtins.input', lambda _: '~/test1')
    src = get_dst(name)
    assert src == str(temp_dir / 'test1')