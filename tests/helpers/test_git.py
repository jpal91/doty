import os
import subprocess
import pytest
from pygit2 import Repository, GIT_RESET_HARD
from doty.helpers.git import get_repo, make_commit, parse_status, prior_commit_hex, last_commit_file

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

def test_prior_commit_hex(temp_dir, git_repo):
    repo = git_repo
    last_commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, cwd=temp_dir / 'dotfiles').stdout.decode('utf-8').strip()

    assert repo.head.name == 'refs/heads/main'
    assert str(repo.head.target) == last_commit
    assert prior_commit_hex(repo) == last_commit

def test_last_commit_file(temp_dir, git_repo):
    def get_commit_file(commit: str) -> str:
        return subprocess.run(['git', 'show', f'{commit}:.doty_config/doty_lock.yml'], capture_output=True, cwd=temp_dir / 'dotfiles').stdout.decode('utf-8').strip()
    last_commit = prior_commit_hex(git_repo)
    commit_file = get_commit_file(last_commit)

    assert commit_file == ""
    assert commit_file == git_repo[last_commit].tree['.doty_config/doty_lock.yml'].data.decode('utf-8')
    assert commit_file == last_commit_file('.doty_config/doty_lock.yml')

    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'
    with open(doty_lock_path, 'a') as f:
        f.write('test')
    
    make_commit(git_repo, 'test commit')
    new_commit = prior_commit_hex(git_repo)
    commit_file = get_commit_file(new_commit)

    assert commit_file == "test"
    assert commit_file == git_repo[new_commit].tree['.doty_config/doty_lock.yml'].data.decode('utf-8')
    assert commit_file == last_commit_file('.doty_config/doty_lock.yml')

    with open(doty_lock_path, 'a') as f:
        f.write('test2')
    

    assert last_commit_file('.doty_config/doty_lock.yml') == "test"

    # assert str(git_repo.head.target) == new_commit
    # Cleanup - revert to last_commit with pygit2
    git_repo.reset(last_commit, GIT_RESET_HARD)
    
    # assert str(git_repo.head.target) == last_commit
    # assert last_commit_file('.doty_config/doty_lock.yml') == ""
