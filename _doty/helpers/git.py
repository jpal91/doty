import os
from pygit2 import Repository, Signature

def get_repo(path: str) -> Repository:
    return Repository(path)

def get_status(repo: Repository) -> dict:
    return repo.status()

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