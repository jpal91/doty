import os
from pygit2 import Repository, Signature, GIT_CHECKOUT_FORCE

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

def prior_commit_hex(repo: Repository) -> str:
    head_commit = repo[repo.head.target]
    return head_commit.hex

def last_commit_file(file_name: str) -> str:
    repo = get_repo()

    last_commit = repo[prior_commit_hex(repo)]
    
    try:
        file = last_commit.tree[file_name].data.decode('utf-8')
    except KeyError:
        file = ''

    return file

def checkout(repo: Repository, branch: str, override: bool = True) -> bool:
    branch = 'refs/heads/' + branch
    checkout_branch = repo.branches.local.get(branch)
    last_commit = repo[prior_commit_hex(repo)]

    if checkout_branch:
        if override:
            repo.branches.local.delete(branch)
            new_branch = repo.branches.local.create(branch, last_commit)
            repo.checkout(new_branch)
        else:
            return False
        
    else:
        new_branch = repo.branches.local.create(branch, last_commit)
        repo.checkout(new_branch)

    return True
    

if __name__ == '__main__':
    print(last_commit_file('bash/.bashrc.1'))