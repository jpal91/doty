import os
import pytest
import signal
from doty.add import get_user_input, double_check, get_name, get_src, find_src, check_dst, get_dst, add_doty_ignore, get_confirm_str, add


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
        ('dotfiles/.dot_file1', True),
        (".good_entry2", False),
        (".good_entry3", False),
        ("~/.good_entry4", False),
        ("~/dotfiles/../.good_entry4", False),
    ]
)
def test_find_src(temp_dir, input, error):
    home = temp_dir
    
    # If error is true, the src is bad and is expected to fail and return an empty string
    if error:
        src = find_src(input)
        assert src == ""
    else:
        src = find_src(input)
        # assert src == str(home / input)
        assert src != ''
    

@pytest.mark.parametrize(
    "input,expected",
    [
        (
            ["", ".good_entry1"],
            "\033[1;31mSource path cannot be empty, please try again.\033[0m\n",
        ), # Tests error on no input, then valid input
        ([".good_entry1"], ""), # Tests valid input
        (
            ['.bad_entry1', '.good_entry1'],
            "\033[1;31mSource path does not exist, please try again.\033[0m\n",
        ), # Tests error on bad input, then valid input
        (
            ['dotfiles/.dot_file1', '.good_entry1'],
            "\033[1;31mSource path cannot be in dotfiles directory, please try again.\033[0m\n",
        ) # Tests error on input being in dotfiles directory, then valid input
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
    "input,error",
    [
        ('.good_entry1', False), # Tests valid input
        ('bash/.good_entry1', False),
        ('~/dotfiles/.good_entry1', False),
        ('home/user', False),
        ('/home/user', True), # Tests bad input, path is absolute and not in dotfiles directory
        ('.dot_file1', True), # Tests bad input, path exists
    ]
)
def test_check_dst(temp_dir, input, error):
    if error:
        dst = check_dst(input)
        assert dst == ''
    else:
        dst = check_dst(input)
        if input.startswith('~/dotfiles/'):
            input = input.replace('~/dotfiles/', '')
        assert dst == str(temp_dir / 'dotfiles' / input)

@pytest.mark.parametrize(
    "input,expected,error",
    [
        ('', '.good_entry1', ''), # Test user not inputing any name, which defaults the file path to the same as 'name'
        ('test', 'test', ''), # Tests user input which will set path same to user input
        ('dotfiles/.dot_file1', 'dotfiles/.dot_file1', ''),
        (['.dot_file1', '.dot_file1.alt'], '.dot_file1.alt', '\033[1;31mDestination path already exists, please try again.\033[0m\n'), # Tests path already existing error
    ],
)
def test_get_dst(temp_dir, input, error, expected, monkeypatch, capfd):
    inputs = iter(input if isinstance(input, list) else [input])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    name = get_dst('.good_entry1', check=False)
    err = capfd.readouterr().err
    assert name == str(temp_dir / 'dotfiles' / expected)
    assert err ==  error

def test_add_doty_ignore(temp_dir):
    dotyignore_path = temp_dir / 'dotfiles' / '.doty_config' / '.dotyignore'

    with open(dotyignore_path, 'w') as f:
        f.write('')

    add_doty_ignore('.ignore_entry')

    with open(dotyignore_path, 'r') as f:
        current = f.readlines()
    
    assert current == ['.ignore_entry\n']

def test_get_confirm_str(temp_dir):
    name = 'test'
    src = str(temp_dir / '.dot_file1')
    dst = str(temp_dir / 'dotfiles' / '.dot_file1')
    linked = 'False'

    expected = f'\n\n\033[1;34mName:\033[0m  \033[1;37m{name}\n\033[1;34mSource:\033[0m  \033[1;37m{src}\n\033[1;34mDestination:\033[0m  \033[1;37m{dst}\n\033[1;34mLinked:\033[0m  \033[1;37m{linked}\n'

    assert get_confirm_str(name, src, dst, linked) == expected

@pytest.mark.parametrize(
    'keyargs,expected',
    [
        ({ 'entry_name': '.good_entry1', 'src': '.good_entry1', 'dst': '.good_entry1' }, 'COMPLETE'),
        ({ 'entry_name': '.good_entry1', 'src': '.good_entry1', 'dst': '.good_entry1', 'force': True }, 'COMPLETE'),
        ({ 'entry_name': '.good_entry1', 'src': '', 'dst': '.good_entry1', 'no_link': False }, 'COMPLETE'),
        ({ 'entry_name': '', 'src': '.good_entry1', 'dst': '.good_entry1', 'no_link': True }, 'COMPLETE'),
        ({ 'entry_name': '.good_entry1', 'src': '.good_entry1', 'dst': '' }, 'COMPLETE'),
        ({ 'entry_name': '', 'src': '', 'dst': '', 'no_link': False }, 'COMPLETE'),
        ({ 'entry_name': '.bad_entry1', 'src': '', 'dst': '.bad_entry1' }, 'EXIT1'),
        ({ 'entry_name': '.bad_entry1', 'src': '.bad_entry1', 'dst': '' }, 'EXIT1'),
        ({ 'entry_name': '.good_entry1', 'src': '.good_entry1', 'dst': '.good_entry1' }, 'EXIT0'),
        ({ 'entry_name': '.good_entry1', 'dst': '.good_entry1' }, 'EXIT00'),
        ({ 'entry_name': '.good_entry1', 'src': '.good_entry1', 'dst': '.good_entry1' }, 'EXIT000'),
    ]
)
def test_add(temp_dir, tmp_path_factory, keyargs, expected, monkeypatch):
    monkeypatch.setattr('doty.add.move_file', lambda *_: None)
    monkeypatch.setattr('doty.add.update', lambda **_: None)
    
    # Tests multiple kwargs to add which will result in a entry being succesfully added
    if expected == 'COMPLETE':
        monkeypatch.setattr('doty.add.double_check', lambda *_: True)
        name, src, dst = '.good_entry1', str(temp_dir / '.good_entry1'), str(temp_dir / 'dotfiles' / '.good_entry1')
        linked = not keyargs['no_link'] if 'no_link' in keyargs else True

        if not keyargs['entry_name']:
            monkeypatch.setattr('doty.add.get_name', lambda **_: name)
        
        if not keyargs['src']:
            monkeypatch.setattr('doty.add.get_src', lambda **_: src)
        
        if not keyargs['dst']:
            monkeypatch.setattr('doty.add.get_dst', lambda *_, **__: dst)
        
        res = add(**keyargs)

        assert res['name'] == name
        assert res['src'] == src
        assert res['dst'] == dst
        assert res['linked'] == linked
    
    # Tests instances where the function would exit with a code of 1
    # Specifically when a user inputs a bad src or dst
    elif expected == 'EXIT1':
        monkeypatch.setattr('doty.add.double_check', lambda *_: True)

        if not keyargs['src']:
            monkeypatch.setattr('doty.add.get_src', lambda **_: '')
            monkeypatch.setattr('doty.add.check_dst', lambda *_: '')
        
        if not keyargs['dst']:
            monkeypatch.setattr('doty.add.get_dst', lambda *_, **__: '')
            monkeypatch.setattr('doty.add.find_src', lambda *_: '')

        with pytest.raises(SystemExit) as exit:
            add(**keyargs)
        
        assert exit.type == SystemExit
        assert exit.value.code == 1

    # Tests instances where the function would exit with a code of 0
    # Specifically when a user aborts the process by not confirming 'y' to the double_check confirmation
    elif expected == 'EXIT0':
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        with pytest.raises(SystemExit) as exit:
            add(**keyargs)
        
        assert exit.type == SystemExit
        assert exit.value.code == 0
    
    
    elif expected == 'EXIT00':
        non_home = tmp_path_factory.mktemp('non-home-dir')
        (non_home / '.good_entry1').touch()
        inp = iter(['', 'n'])
        monkeypatch.setattr('builtins.input', lambda _: next(inp))

        with pytest.raises(SystemExit) as exit:
            add(**keyargs, src=str(non_home / '.good_entry1'))
        
        assert exit.type == SystemExit
        assert exit.value.code == 0

    # Same as EXIT0 but exits on the second instance of double_check when the user is asked to confirm
    #   the entire entry looks correct, after get_confirm_str is called
    elif expected == 'EXIT000':
        inp = iter(['', '', 'n'])
        monkeypatch.setattr('builtins.input', lambda _: next(inp))

        with pytest.raises(SystemExit) as exit:
            add(**keyargs)
        
        assert exit.type == SystemExit
        assert exit.value.code == 0