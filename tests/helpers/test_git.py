import os
import pytest
from pygit2 import Repository
from doty.helpers.git import get_repo, make_commit, parse_status

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({'HOME': str(temp_dir)})

def test_get_repo(setup, temp_dir, git_repo):
    repo = get_repo()
    assert isinstance(repo, Repository)
    assert repo.path == str(temp_dir / 'dotfiles' / '.git') + '/'
    assert repo.path == git_repo.path
    assert repo.head.name == 'refs/heads/main'

def test_make_commit(setup, temp_dir, git_repo):
    repo = git_repo

    assert repo.status() == {}
    assert repo.head.peel().message == 'initial commit'
    make_commit(repo, 'test commit')
    
    assert repo.status() == {}
    assert repo.head.name == 'refs/heads/main'
    assert repo.head.peel().message == 'test commit'

    (temp_dir / 'dotfiles' / '.dot_file7').touch()

    assert repo.status() == {'.dot_file7': 128}
    make_commit(repo, 'test commit 2')

    assert repo.status() == {}
    assert repo.head.name == 'refs/heads/main'
    assert repo.head.peel().message == 'test commit 2'

def test_parse_status(temp_dir, git_repo):
    repo = git_repo

    assert repo.status() == {}
    assert parse_status(repo) == ''

    (temp_dir / 'dotfiles' / '.dot_file8').touch()
    assert repo.status() == {'.dot_file8': 128}
    assert parse_status(repo) == ' | Files(A1|R0|M0)'
    
    (temp_dir / 'dotfiles' / '.dot_file7').unlink()
    assert repo.status() == {'.dot_file8': 128, '.dot_file7': 512}
    assert parse_status(repo) == ' | Files(A1|R1|M0)'

    with open(temp_dir / 'dotfiles' / 'dot_dir' / '.dot_file6', 'a') as f:
        f.write('test')
    
    assert repo.status() == {'.dot_file8': 128, '.dot_file7': 512, 'dot_dir/.dot_file6': 256}
    assert parse_status(repo) == ' | Files(A1|R1|M1)'