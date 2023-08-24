import os
from pygit2 import Repository, Signature

def get_repo() -> Repository:
    path = os.path.join(os.environ['HOME'], 'dotfiles', '.git')
    return Repository(path)

def make_commit(repo: Repository, message: str) -> str:
    index = repo.index
    ref = repo.head.name
    parent = [repo.head.target]
    index.add_all()
    index.write()
    tree = index.write_tree()
    author_commiter = Signature(os.getenv('GIT_AUTHOR_NAME', 'doty'), os.getenv('GIT_AUTHOR_EMAIL', 'doty@email.com'))
    commit = repo.create_commit(ref, author_commiter, author_commiter, message, tree, parent)

    return commit