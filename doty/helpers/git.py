import os
from pygit2 import Repository, Signature, Commit, GIT_SORT_TIME, GIT_SORT_REVERSE

class DirtyRepoError(Exception):
    pass

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

def find_last_commit(repo: Repository, file_path: str) -> Commit:
    last_commit = None

    for commit in repo.walk(repo.head.target, GIT_SORT_TIME | GIT_SORT_REVERSE):
        diff = repo.diff(commit.parents[0], commit) if commit.parents else commit.tree.diff_to_tree()

        for patch in diff:
            print(commit.hex, commit.message, patch.delta.old_file.path, patch.delta.new_file.path)
            if patch.delta.old_file.path == file_path or patch.delta.new_file.path == file_path:
                last_commit = commit
                break

        if last_commit:
            break

    return last_commit

def last_commit_file(file_name: str) -> str:
    repo = get_repo()

    last_commit = repo[prior_commit_hex(repo)]
    
    try:
        file = last_commit.tree[file_name].data.decode('utf-8')
    except KeyError:
        file = ''

    return file

def last_commit_file2(repo: Repository, file_name: str) -> str:
    last_commit = find_last_commit(repo, file_name)

    if not last_commit:
        return ''

    print('here')
    try:
        file = last_commit.tree[file_name].data.decode('utf-8')
    except KeyError:
        print('keyerror')
        file = ''
    
    return file

def checkout(repo: Repository, branch_name: str, override: bool = False) -> bool:
    checkout_branch = repo.branches.get(branch_name)
    last_commit = repo[prior_commit_hex(repo)]

    if repo.status() and not override:
        raise DirtyRepoError('Cannot checkout branch with dirty repo')

    if checkout_branch:
        if override and branch_name != 'main':
            repo.branches.delete(branch_name)
            new_branch = repo.branches.local.create(branch_name, last_commit)
            repo.checkout(new_branch)
        else:
            repo.checkout(checkout_branch)
    else:
        new_branch = repo.branches.local.create(branch_name, last_commit)
        repo.checkout(new_branch)

    return True
    

if __name__ == '__main__':
    print(last_commit_file('bash/.bashrc.1'))