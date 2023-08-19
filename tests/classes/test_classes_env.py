import os

def test_env(temp_dir, load_env):
    assert os.environ['DOTHOME'] == str(temp_dir)
    assert os.environ['DOTY_DIR'] == str(temp_dir / 'dotfiles')
    assert os.environ['DPATH'] == str(temp_dir / 'dotfiles')
    assert os.environ['DOTY_LOG_PATH'] == str(temp_dir / 'dotfiles' / 'logs' / 'doty.log')