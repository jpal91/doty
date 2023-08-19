import pytest
from dotenv import load_dotenv

def create_dummy_home_files(home_dir):
    (home_dir / '.bashrc').touch()
    (home_dir / '.zshrc').touch()
    (home_dir / '.zsh_history').touch()

def create_dummy_doty_files(doty_dir):
    (doty_dir / 'dotycfg.yml').touch()
    (doty_dir / 'doty_lock.yml').touch()
    (doty_dir / 'logs' / 'doty.log').touch()

def create_dotyrc(home, doty, cfg, logs):
    dotyrc = cfg / 'dotyrc'
    dotyrc.touch()

    envs = [
        f'DOTHOME="{home}"',
        f'DOTY_DIR="{doty}"',
        f'DPATH="{doty}"',
        f'DOTY_LOG_PATH="{logs}/doty.log"',
    ]

    with open(dotyrc, 'w') as f:
        f.write('\n'.join(envs))

@pytest.fixture(scope='session')
def temp_dir(tmp_path_factory):
    home_dir = tmp_path_factory.mktemp('home')
    dot_dir = home_dir / 'dotfiles'
    dot_dir.mkdir()
    cfg_dir = home_dir / '.config' / 'doty'
    cfg_dir.mkdir(parents=True)
    log_dir = dot_dir / 'logs'
    log_dir.mkdir()

    # Create dummy files
    create_dummy_home_files(home_dir)
    create_dummy_doty_files(dot_dir)
    create_dotyrc(home_dir, dot_dir, cfg_dir, log_dir)

    return home_dir

@pytest.fixture(autouse=True, scope='session')
def load_env(temp_dir):
    load_dotenv(temp_dir / '.config' / 'doty' / 'dotyrc')