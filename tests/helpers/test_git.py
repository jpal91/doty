import os
import pytest
from pygit2 import Repository
from doty.helpers.git import get_repo, make_commit

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir):
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