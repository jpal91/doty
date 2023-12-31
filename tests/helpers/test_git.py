import os
import subprocess
import pytest
from pygit2 import Repository, GIT_RESET_HARD
from doty.helpers.git import get_repo, make_commit, parse_status, prior_commit_hex, last_commit_file, checkout, find_last_commit, last_commit_file2, DirtyRepoError

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({'HOME': str(temp_dir)})

@pytest.fixture(scope='module')
def first_commit(git_repo):
    return git_repo.head.target

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

@pytest.mark.skip()
def test_find_last_commit(temp_dir, git_repo, first_commit, dummy_files):
    # with open(temp_dir / 'dotfiles' / '.dot_file7', 'a') as f:
    #     f.write('test')
    # make_commit(git_repo, 'test commit 3')
    with open(temp_dir / 'dotfiles' / '.dot_file7', 'a') as f:
        f.write('test2')

    make_commit(git_repo, 'test commit 4')
    last_commit = git_repo.head.target

    for i in range(5,9):
        next_commit = make_commit(git_repo, f'test commit {i}')
    
    assert git_repo.head.target == next_commit
    assert git_repo.head.peel().message == 'test commit 8'

    for ref in git_repo.references['refs/heads/main'].log():
        print(ref.oid_old, ref.oid_new, ref.message)
    
    last_change_commit = find_last_commit(git_repo, '.dot_file7')
    assert last_change_commit.hex == last_commit.hex
    assert last_change_commit.message == 'test commit 4'

@pytest.mark.skip()
def test_last_commit_file2(temp_dir, git_repo):
    assert git_repo.head.peel().message == 'test commit 8'
    # make_commit(git_repo, 'test commit 9')
    assert last_commit_file2(git_repo, '.dot_file7') == 'test2'
    
    with open(temp_dir / 'dotfiles' / '.dot_file7', 'a') as f:
        f.write('test3')
    
    make_commit(git_repo, 'test commit 9')
    assert git_repo.head.peel().message == 'test commit 9'

    with open(temp_dir / 'dotfiles' / '.dot_file7', 'a') as f:
        f.write('test4')

    assert last_commit_file2(git_repo, '.dot_file7') == 'test2test3'

    assert last_commit_file2(git_repo, 'never_existed') == ''

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

def test_checkout_new_branch(temp_dir, git_repo: Repository):
    repo = git_repo
    last_commit = prior_commit_hex(repo)
    assert repo.head.name == 'refs/heads/main'
    assert str(repo.head.target) == last_commit
    assert last_commit_file('.doty_config/doty_lock.yml') == ""

    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'
    with open(doty_lock_path, 'a') as f:
        f.write('test')
    
    make_commit(repo, 'test commit')
    new_commit = prior_commit_hex(repo)
    assert str(repo.head.target) == new_commit
    assert last_commit_file('.doty_config/doty_lock.yml') == "test"

    res = checkout(repo, 'temp_branch')
    assert res == True
    assert repo.branches.local['temp_branch'].target == repo.head.target
    assert repo.branches['temp_branch'].name == 'refs/heads/temp_branch'
    assert str(repo.head.target) == new_commit
    assert last_commit_file('.doty_config/doty_lock.yml') == "test"

def test_checkout_with_branch_edits(temp_dir, git_repo: Repository):
    repo = git_repo
    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'
    new_commit = prior_commit_hex(repo)

    with open(doty_lock_path, 'a') as f:
        f.write('test2')

    assert last_commit_file('.doty_config/doty_lock.yml') == "test"
    make_commit(repo, 'test commit 2')
    new_branch_commit = prior_commit_hex(repo)

    # checkout(repo, 'temp_branch')
    assert str(repo.head.target) == new_branch_commit
    assert last_commit_file('.doty_config/doty_lock.yml') == "testtest2"

    (temp_dir / 'dotfiles' / 'checkout_test_file.txt').touch()

    make_commit(repo, 'test commit 3')
    new_branch_commit = prior_commit_hex(repo)
    assert str(repo.head.target) == new_branch_commit
    assert last_commit_file('.doty_config/doty_lock.yml') == "testtest2"
    assert (temp_dir / 'dotfiles' / 'checkout_test_file.txt').exists()

    res = checkout(repo, 'main')
    assert res == True
    assert repo.branches['main'].target == repo.head.target
    assert repo.head.peel().message == 'test commit' 
    assert str(repo.head.target) == new_commit
    assert last_commit_file('.doty_config/doty_lock.yml') == "test"
    assert not (temp_dir / 'dotfiles' / 'checkout_test_file.txt').exists()

def test_checkout_with_override(temp_dir, git_repo: Repository):
    repo = git_repo
    doty_lock_path = temp_dir / 'dotfiles' / '.doty_config' / 'doty_lock.yml'
    new_commit = prior_commit_hex(repo)

    assert repo.branches['main'].target == repo.head.target
    assert not (temp_dir / 'dotfiles' / 'checkout_test_file_1.txt').exists()

    (temp_dir / 'dotfiles' / 'checkout_test_file_1.txt').touch()
    with open(doty_lock_path, 'a') as f:
        f.write('test3')

    new_commit = make_commit(repo, 'test commit 4')
    assert repo.head.peel().message == 'test commit 4' 
    assert last_commit_file('.doty_config/doty_lock.yml') == "testtest3"

    res = checkout(repo, 'temp_branch', override=True)
    assert res is True
    assert repo.branches.local['temp_branch'].target == repo.head.target
    assert repo.branches['temp_branch'].name == 'refs/heads/temp_branch'
    assert repo.head.peel().message == 'test commit 4' 
    assert repo.head.target == new_commit
    assert (temp_dir / 'dotfiles' / 'checkout_test_file_1.txt').exists()
    assert not (temp_dir / 'dotfiles' / 'checkout_test_file.txt').exists()
    assert last_commit_file('.doty_config/doty_lock.yml') == "testtest3"

def test_checkout_with_error(temp_dir, git_repo: Repository):
    repo = git_repo
    last_commit = prior_commit_hex(repo)

    checkout(repo, 'main')
    assert repo.status() == {}
    assert repo.branches.local['main'].target == repo.head.target
    assert str(repo.head.target) == last_commit
    assert repo.head.peel().message == 'test commit 4' 
    assert (temp_dir / 'dotfiles' / 'checkout_test_file_1.txt').exists()
    with open(temp_dir / 'dotfiles' / 'checkout_test_file_1.txt') as f:
        assert f.read() == ''

    with open(temp_dir / 'dotfiles' / 'checkout_test_file_1.txt', 'a') as f:
        f.write('test changes')
    assert repo.status() != {}

    with pytest.raises(DirtyRepoError) as ex:
        checkout(repo, 'temp_branch')
    assert repo.branches.local['main'].target == repo.head.target

    checkout(repo, 'temp_branch', override=True)

    assert repo.branches.local['temp_branch'].target == repo.head.target
    assert repo.head.peel().message == 'test commit 4' 
    with open(temp_dir / 'dotfiles' / 'checkout_test_file_1.txt') as f:
        assert f.read() == 'test changes'
