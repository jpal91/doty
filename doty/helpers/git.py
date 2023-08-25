import os
from pygit2 import Repository, Signature

def get_repo() -> Repository:
    path = os.path.join(os.environ['HOME'], 'dotfiles', '.git')
    return Repository(path)

def parse_status(repo: Repository) -> str:
    status = repo.status()
    if not status:
        return ''
    
    add, delete, modify = 0, 0, 0

    for flag in status.values():
        if flag & 128:
            add += 1
        if flag & 512:
            delete += 1
        if flag & 256:
            modify += 1
    
    status_str = f' | Files(A{add}|R{delete}|M{modify})'
    return status_str

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