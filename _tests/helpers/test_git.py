import os
import pytest
from pygit2 import Repository
from _doty.helpers.git import make_commit

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir):
    os.environ.update({'HOME': str(temp_dir)})
    git = temp_dir / 'dotfiles' / '.git'
    repo = Repository(str(git))
    yield repo

def test_make_commit(setup, temp_dir):
    repo = setup

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