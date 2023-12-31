import os
import pytest
from doty.update import link_new_files, unlink_files, commit_changes, update
from doty.helpers.git import make_commit
# from doty.classes.DotyLogger import DotyLogger

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({'HOME': str(temp_dir), 'DOTFILES_PATH': str(temp_dir / 'dotfiles'), 'GIT_AUTO_COMMIT': 'false'})
    yield
    with open(temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml', 'w') as f:
        f.write('')

def test_link_new_files(temp_dir):
    df_links = [str(temp_dir / 'dotfiles' / 'dot_dir' / 'dot_file4')]
    
    assert not os.path.islink(str(temp_dir / 'dot_file4'))
    link_new_files(df_links)
    assert os.path.islink(str(temp_dir / 'dot_file4'))
    os.unlink(str(temp_dir / 'dot_file4'))

def test_unlink_files(temp_dir):
    df_unlinks = ['.dot_file3']
    
    assert os.path.islink(str(temp_dir / '.dot_file3'))
    unlink_files(df_unlinks)
    assert not os.path.islink(str(temp_dir / '.dot_file3'))
    (temp_dir / '.dot_file3').symlink_to(temp_dir / 'dotfiles' / 'dot_dir' / '.dot_file3')

def test_commit_changes(temp_dir, git_repo):
    assert git_repo.status() == {}
    link_new_files([str(temp_dir / 'dotfiles' / 'dot_dir' / 'dot_file4')])
    unlink_files(['.dot_file3'])
    assert git_repo.status() == {}

    commit_changes(1, 1)
    assert git_repo.status() == {}
    assert git_repo.head.peel().message == 'Links(A1|R1)'

    (temp_dir / 'dotfiles' / '.dot_file7').touch()
    assert git_repo.status() == {'.dot_file7': 128}
    link_new_files([str(temp_dir / 'dotfiles' / '.dot_file7')])
    assert git_repo.status() == {'.dot_file7': 128}
    commit_changes(1, 0)
    assert git_repo.status() == {}
    assert git_repo.head.peel().message == 'Links(A1|R0) | Files(A1|R0|M0)'

    os.unlink(str(temp_dir / 'dot_file4'))
    (temp_dir / '.dot_file3').symlink_to(temp_dir / 'dotfiles' / 'dot_dir' / '.dot_file3')


def _test_update(temp_dir, git_repo):
    assert not os.path.islink(str(temp_dir / 'dot_file4'))
    update()
    assert os.path.islink(str(temp_dir / 'dot_file4'))
    assert git_repo.head.peel().message == 'Links(A2|R0)'

    di_path = temp_dir / 'dotfiles' / '.doty_config' / '.dotyignore'
    with open(di_path, 'a') as f:
        f.write('\n.dot_file2')
    
    (temp_dir / 'dotfiles' / '.dot_file8').touch()
    assert os.path.islink(str(temp_dir / '.dot_file2'))
    update()
    assert not os.path.islink(str(temp_dir / '.dot_file2'))
    assert git_repo.head.peel().message == 'Links(A1|R1) | Files(A2|R0|M0)'
    (temp_dir / '.dot_file2').symlink_to(temp_dir / 'dotfiles' / '.dot_file2')


def _test_update_flags(temp_dir, git_repo):
    assert git_repo.head.peel().message == 'Links(A1|R1) | Files(A2|R0|M0)'
    (temp_dir / 'dotfiles' / '.dot_file9').touch()
    update(commit=False)
    assert git_repo.head.peel().message == 'Links(A1|R1) | Files(A2|R0|M0)'
    assert git_repo.status() == {'.dot_file9': 128}
    assert os.path.islink(str(temp_dir / '.dot_file9'))

    with open(temp_dir / 'dotfiles' / '.doty_config' / '.dotyignore', 'a') as f:
        f.write('\n.dot_file9')

    (temp_dir / 'dotfiles' / '.dot_file10').touch()
    update(dry_run=True)
    assert git_repo.head.peel().message == 'Links(A1|R1) | Files(A2|R0|M0)'
    assert git_repo.status() == {'.dot_file9': 128, '.dot_file10': 128, '.doty_config/.dotyignore': 256}
    assert not os.path.islink(str(temp_dir / '.dot_file10'))
    assert os.path.islink(str(temp_dir / '.dot_file9'))

def test_update(temp_dir, git_repo, capfd):    
    # Run once with no assertions to reset
    update()
    capfd.readouterr().err
    
    update()
    out = capfd.readouterr().err
    assert 'No changes detected' in out
    assert not 'Committing changes' in out

    update(quiet=True)
    out = capfd.readouterr().err
    assert out == ''

    (temp_dir / '.dot_file8').touch()
    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'
    with open(doty_lock_path, 'a') as f:
        f.write('- .dot_file8')

    last_commit_message = git_repo.head.peel().message
    update(dry_run=True)
    out = capfd.readouterr().err
    assert 'Added\x1b[0m Files: 1 Links: 1' in out
    assert 'Modified\x1b[0m Files: 1' in out
    assert not 'Committing changes' in out
    assert git_repo.head.peel().message == last_commit_message

    update()
    out = capfd.readouterr().err
    assert 'Added\x1b[0m Files: 1 Links: 1' in out
    assert 'Modified\x1b[0m Files: 1' in out
    assert 'Committing changes' in out
    assert git_repo.head.peel().message == 'Links (A1|R0|U0) | Files (A1|R0|U0|M1)'