import os
import pytest
import pygit2


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    home = tmp_path_factory.mktemp('dotytmp')
    dotfiles = home / 'dotfiles'
    dotfiles.mkdir()
    doty_config = dotfiles / '.doty_config'
    doty_config.mkdir()
    doty_lock = doty_config / 'doty_lock.yml'
    doty_lock.touch()
    gitignore = dotfiles / '.gitignore'

    with open(gitignore, 'w') as f:
        f.write('doty.log')

    for i in range(5):
        entry = home / f'.good_entry{i}'
        entry.touch()

    # os.environ.update({"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles")})
    return home

# @pytest.fixture(scope='session')
# def env(temp_dir, monkeypatch):
#     monkeypatch.setenv('HOME', str(temp_dir))
#     monkeypatch.setenv('DOTFILES_PATH', str(temp_dir / 'dotfiles'))
#     monkeypatch.setenv('DOTY_LOG_PATH', str(temp_dir / 'dotfiles' / '.doty_config' / 'doty.log'))
#     yield

@pytest.fixture(scope='module')
def git_repo(temp_dir):
    dotfiles = temp_dir / 'dotfiles'
    repo = pygit2.init_repository(str(dotfiles))
    ref = 'HEAD'
    index = repo.index
    index.add_all()
    index.write()
    tree = index.write_tree()
    author_commiter = pygit2.Signature('doty', 'email@email.com')
    first_commit = repo.create_commit(ref, author_commiter, author_commiter, 'initial commit', tree, [])
    # repo.branches.get('master').rename('main')
    # print(list(repo.branches))

    yield repo
    main_branch = repo.branches.get('main')
    if main_branch:
        repo.checkout(main_branch)
        repo.reset(first_commit, pygit2.GIT_RESET_HARD)
        print(repo.head.shorthand)

@pytest.fixture(scope='module')
def dummy_files(temp_dir):
    dotfiles = temp_dir / 'dotfiles'
    (dotfiles / '.dot_file1').touch()
    (dotfiles / '.dot_file2').touch()
    (dotfiles / 'dot_dir').mkdir(exist_ok=True)
    (dotfiles / 'dot_dir' / '.dot_file3').touch()
    (dotfiles / 'dot_dir' / 'dot_file4').touch()
    (dotfiles / 'dot_dir' / '.dot_file6').touch()
    (temp_dir / '.dot_file1').symlink_to(dotfiles / '.dot_file1')
    (temp_dir / '.dot_file2').symlink_to(dotfiles / '.dot_file2')
    (temp_dir / '.dot_file3').symlink_to(dotfiles / 'dot_dir' / '.dot_file3')
    (temp_dir / '.dot_file5').touch()
    
    for i in range(5):
        entry = temp_dir / f'.good_entry{i}'
        entry.touch()

    yield

    # Cleanup all created files
    for root, dirs, files in os.walk(temp_dir):
        if '.doty_config' in dirs:
            dirs.remove('.doty_config')
        for file in files:
            if file == '.dotyignore':
                continue
            os.remove(os.path.join(root, file))
    
    doty_ignore = temp_dir / 'dotfiles' / '.doty_config' / '.dotyignore'
    if os.path.exists(doty_ignore):
        os.unlink(doty_ignore)


