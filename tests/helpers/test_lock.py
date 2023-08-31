import os
from pathlib import Path
import pytest
import yaml
from pygit2 import GIT_RESET_HARD
from doty.helpers.lock import parse_entries, get_lock_files, get_lock_file_diff, handle_prior_lock_changes, handle_current_lock_changes, compare_lock_yaml
from doty.classes.entry import DotyEntry
from doty.helpers.git import make_commit, prior_commit_hex, last_commit_file

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update({"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles")})

@pytest.fixture
def lock_file(temp_dir: Path, git_repo):
    doty_lock_path = temp_dir / "dotfiles" / ".doty_config" / "doty_lock.yml"
    current_commit = prior_commit_hex(git_repo)

    with open(doty_lock_path, 'w') as f:
        f.write(f"""\
- name: .bashrc
- .zshrc
- name: .wshrc
  src: {temp_dir}/.wshrc
  dst: {temp_dir}/dotfiles/.wshrc
  linked: true
  link_name: .wshrc
""")
    yield doty_lock_path

    with open(doty_lock_path, 'w') as f:
        f.write('')
    
    if prior_commit_hex(git_repo) != current_commit:
        git_repo.reset(current_commit, GIT_RESET_HARD)

@pytest.mark.parametrize(
    'input,expected',
    [
        (['.bashrc', '.zshrc', { 'name': '.wshrc' }], 3),
        (['.bashrc', '.zshrc', { 'name': '.wshrc', 'src': '/home/user/wshrc' }], 3),
        (['.bashrc', '.zshrc', { 'name': '.wshrc' }, ('bad', 'entry')], 3),
    ]
)
def test_parse_entry(input, expected):
    entries = parse_entries(input)
    assert len(entries) == expected
    assert all([isinstance(entry, dict) for entry in entries])
    assert all(['name' in entry for entry in entries])

def test_get_lock_files(temp_dir: Path, git_repo, lock_file):
    prior_yaml, current_yaml = get_lock_files(lock_file)
    current = [
        {'name': '.bashrc'},
        {'name': '.zshrc'},
        {
            'name': '.wshrc',
            'src': f'{temp_dir}/.wshrc',
            'dst': f'{temp_dir}/dotfiles/.wshrc',
            'linked': True,
            'link_name': '.wshrc'
        }
    ]


    assert prior_yaml == []
    assert current_yaml == current

    with open(lock_file, 'w') as f:
        yaml.safe_dump(current, f)

    make_commit(git_repo, 'test commit')

    with open(lock_file, 'a') as f:
        f.write('- name: .dot_file7')

    new_current = [*current, { 'name': '.dot_file7' }]

    prior_yaml, current_yaml = get_lock_files(lock_file)

    assert prior_yaml == current
    assert current_yaml == new_current

def test_get_lock_file_diff(temp_dir: Path, git_repo, lock_file):
    prior_yaml, current_yaml = get_lock_files(lock_file)
    current = [
        {'name': '.bashrc'},
        {'name': '.zshrc'},
        {
            'name': '.wshrc',
            'src': f'{temp_dir}/.wshrc',
            'dst': f'{temp_dir}/dotfiles/.wshrc',
            'linked': True,
            'link_name': '.wshrc'
        }
    ]

    assert prior_yaml == []
    assert current_yaml == current

    current_entries = [DotyEntry(entry) for entry in current]

    diff_current, diff_prior = get_lock_file_diff(current_entries, [])

    assert diff_current == current_entries
    assert diff_prior == []

    with open(lock_file, 'w') as f:
        yaml.safe_dump([entry.get_vals() for entry in current_entries], f, sort_keys=False)

    make_commit(git_repo, 'test commit')

    with open(lock_file) as f:
        yml = yaml.safe_load(f)

    yml[0]['src'] = '/home/user/.bashrc'
    yml.append({ 'name': '.dot_file7' })

    with open(lock_file, 'w') as f:
        yaml.safe_dump(yml, f, sort_keys=False)
    
    prior_yaml, current_yaml = get_lock_files(lock_file)

    prior_entries = [DotyEntry(entry) for entry in prior_yaml]
    new_current_entries = [DotyEntry(entry) for entry in current_yaml]
    expected_diff_prior = [entry for entry in current_entries if entry.name == '.bashrc']
    expected_diff_current = [DotyEntry(yml[0]), DotyEntry({ 'name': '.dot_file7' })]

    diff_current, diff_prior = get_lock_file_diff(new_current_entries, prior_entries)

    assert diff_prior == expected_diff_prior
    assert diff_current == expected_diff_current

def test_handle_prior_lock_changes(temp_dir: Path, capfd):
    # Testing errors
    # Testing file is not in dst
    lock_changes = [DotyEntry({ 'name' : '.good_entry1', 'linked': False })]
    assert not os.path.exists(temp_dir / 'dotfiles' / '.good_entry1')
    handle_prior_lock_changes(lock_changes)
    err = capfd.readouterr().err
    assert 'Error' in err
    assert 'does not exist' in err

    # Testing there is a file or symlink matching src path which would overwrite
    assert os.path.exists(temp_dir / '.good_entry1')
    (temp_dir / 'dotfiles' / '.good_entry1').touch()
    handle_prior_lock_changes(lock_changes)
    err = capfd.readouterr().err
    assert 'Error' in err
    assert 'already exists' in err

    # Test regular functionality
    lock_changes = [DotyEntry({ 'name' : '.good_entry1', 'linked': True })]
    (temp_dir / '.good_entry1').unlink()
    (temp_dir / '.good_entry1').symlink_to(temp_dir / 'dotfiles' / '.good_entry1')
    assert os.path.islink(temp_dir / '.good_entry1')
    assert os.path.isfile(temp_dir / 'dotfiles' / '.good_entry1')
    handle_prior_lock_changes(lock_changes)
    assert not os.path.islink(temp_dir / '.good_entry1')
    assert not os.path.isfile(temp_dir / 'dotfiles' / '.good_entry1')
    assert os.path.isfile(temp_dir / '.good_entry1')

    # Test regular functionality with link_name
    lock_changes = [DotyEntry({ 'name' : '.good_entry1', 'linked': True, 'link_name': '.good_entry_unique' })]
    (temp_dir / '.good_entry1').rename(temp_dir / 'dotfiles' / '.good_entry1')
    (temp_dir / '.good_entry_unique').symlink_to(temp_dir / 'dotfiles' / '.good_entry1')
    assert os.path.islink(temp_dir / '.good_entry_unique')
    assert os.readlink(temp_dir / '.good_entry_unique') == str(temp_dir / 'dotfiles' / '.good_entry1')
    assert os.path.isfile(temp_dir / 'dotfiles' / '.good_entry1')
    handle_prior_lock_changes(lock_changes)
    assert not os.path.islink(temp_dir / '.good_entry_unique')
    assert not os.path.isfile(temp_dir / 'dotfiles' / '.good_entry1')
    assert os.path.isfile(temp_dir / '.good_entry1')

def test_handle_current_lock_changes(temp_dir: Path, capfd):
    # Testing errors
    # Testing file is not in src
    locked_entries = [DotyEntry({ 'name' : '.good_entry_no_exist', 'linked': False })]
    assert not os.path.exists(temp_dir / '.good_entry_no_exist')
    handle_current_lock_changes(locked_entries)
    err = capfd.readouterr().err
    assert 'Error' in err
    assert 'does not exist' in err

    # Testing file is in src but is symlink
    (temp_dir / '.good_entry_no_exist').symlink_to(temp_dir / 'dotfiles' / '.dot_file1')
    assert os.path.exists(temp_dir / '.good_entry_no_exist')
    assert os.path.islink(temp_dir / '.good_entry_no_exist')
    handle_current_lock_changes(locked_entries)
    err = capfd.readouterr().err
    assert 'Error' in err
    assert 'does not exist' in err
    (temp_dir / '.good_entry_no_exist').unlink()

    # Testing file already exists in dst
    (temp_dir / '.dot_file_new').touch()
    (temp_dir / 'dotfiles' / '.dot_file_new').touch()
    locked_entries = [DotyEntry({ 'name' : '.dot_file_new', 'linked': False })]
    assert os.path.exists(temp_dir / 'dotfiles' / '.dot_file_new')
    assert os.path.exists(temp_dir / '.dot_file_new')
    assert not os.path.islink(temp_dir / '.dot_file_new')
    handle_current_lock_changes(locked_entries)
    err = capfd.readouterr().err
    assert 'Error' in err
    assert 'already exists' in err
    (temp_dir / 'dotfiles' / '.dot_file_new').unlink()

    # Testing if unique link_name already exists in Home directory
    # File will be moved but link won't be created
    locked_entries = [DotyEntry({ 'name' : '.dot_file_new', 'linked': True, 'link_name': '.good_entry0' })]
    assert os.path.exists(temp_dir / '.good_entry0')
    assert not os.path.islink(temp_dir / '.good_entry0')
    assert os.path.exists(temp_dir / '.dot_file_new')
    assert not os.path.islink(temp_dir / '.dot_file_new')
    assert not os.path.exists(temp_dir / 'dotfiles' / '.dot_file_new')
    handle_current_lock_changes(locked_entries)
    err = capfd.readouterr().err
    assert 'Error' in err
    assert str(temp_dir / '.good_entry0') in err
    assert 'already exists' in err
    assert os.path.exists(temp_dir / 'dotfiles' / '.dot_file_new')
    assert not os.path.islink(temp_dir / '.dot_file_new')
    (temp_dir / 'dotfiles' / '.dot_file_new').rename(temp_dir / '.dot_file_new')

    # Test regular functionality
    locked_entries = [DotyEntry({ 'name' : '.dot_file_new', 'linked': True })]
    assert os.path.exists(temp_dir / '.dot_file_new')
    assert not os.path.islink(temp_dir / '.dot_file_new')
    assert not os.path.exists(temp_dir / 'dotfiles' / '.dot_file_new')
    handle_current_lock_changes(locked_entries)
    assert os.path.islink(temp_dir / '.dot_file_new')
    assert os.readlink(temp_dir / '.dot_file_new') == str(temp_dir / 'dotfiles' / '.dot_file_new')
    assert os.path.exists(temp_dir / 'dotfiles' / '.dot_file_new')
    (temp_dir / '.dot_file_new').unlink()
    (temp_dir / 'dotfiles' / '.dot_file_new').rename(temp_dir / '.dot_file_new')

    # Test regular functionality with link_name
    locked_entries = [DotyEntry({ 'name' : '.dot_file_new', 'linked': True, 'link_name': '.dot_file_new_unique' })]
    assert os.path.exists(temp_dir / '.dot_file_new')
    assert not os.path.islink(temp_dir / '.dot_file_new')
    assert not os.path.exists(temp_dir / 'dotfiles' / '.dot_file_new')
    assert not os.path.exists(temp_dir / '.dot_file_new_unique')
    handle_current_lock_changes(locked_entries)
    assert os.path.islink(temp_dir / '.dot_file_new_unique')
    assert os.readlink(temp_dir / '.dot_file_new_unique') == str(temp_dir / 'dotfiles' / '.dot_file_new')
    assert os.path.exists(temp_dir / 'dotfiles' / '.dot_file_new')
    (temp_dir / '.dot_file_new_unique').unlink()
    (temp_dir / 'dotfiles' / '.dot_file_new').rename(temp_dir / '.dot_file_new')

    # Test regular functionality with different src, dst, and link_name
    locked_entries = [DotyEntry({ 'name' : '.dot_file_new', 'src': f'{temp_dir}/.dot_file_new', 'dst': f'{temp_dir}/new-dot-dir/.dot_file_new_dst', 'linked': True, 'link_name': '.dot_file_new_unique' })]
    assert os.path.exists(temp_dir / '.dot_file_new')
    assert not os.path.islink(temp_dir / '.dot_file_new')
    assert not os.path.exists(temp_dir / 'new-dot-dir' / '.dot_file_new_dst')
    assert not os.path.exists(temp_dir / '.dot_file_new_unique')
    handle_current_lock_changes(locked_entries)
    assert os.path.islink(temp_dir / '.dot_file_new_unique')
    assert os.readlink(temp_dir / '.dot_file_new_unique') == str(temp_dir / 'new-dot-dir' / '.dot_file_new_dst')
    assert os.path.exists(temp_dir / 'new-dot-dir' / '.dot_file_new_dst')

def test_compare_lock_yaml(temp_dir: Path, git_repo, lock_file, capfd):
    paths = [
        (temp_dir / '.bashrc'),
        (temp_dir / '.zshrc'),
        (temp_dir / '.wshrc')
    ]

    assert all([not path.exists() for path in paths])
    [p.touch() for p in paths]

    with open(lock_file) as f:
        org_file = yaml.safe_load(f)
    
    entries = [DotyEntry(entry) if isinstance(entry, dict) else DotyEntry({ 'name': entry }) for entry in org_file]
    assert all([not os.path.exists(e.dst) for e in entries])
    
    compare_lock_yaml()
    assert all([os.path.exists(e.dst) for e in entries])
    assert all([os.path.islink(e.src) for e in entries])

    make_commit(git_repo, 'test commit')

    with open(lock_file) as f:
        new_file = yaml.safe_load(f)
    
    assert org_file != new_file
    assert new_file == [e.get_vals() for e in entries]

    new_file[0]['linked'] = False
    new_file[1]['link_name'] = '.zshrc_unique'
    (temp_dir / '.bash_aliases.original').touch()
    new_entry = {
        'name': '.bash_aliases',
        'src': f'{temp_dir}/.bash_aliases.original',
        'dst': f'{temp_dir}/bash/.bash_aliases.1',
        'linked': True,
        'link_name': '.bash_aliases'
    }
    new_file.append(new_entry)

    with open(lock_file, 'w') as f:
        yaml.safe_dump(new_file, f, sort_keys=False)
    
    assert os.path.islink(temp_dir / '.bashrc')
    assert os.path.islink(temp_dir / '.zshrc')
    assert not os.path.islink(temp_dir / '.zshrc_unique')
    assert os.path.exists(temp_dir / '.bash_aliases.original')
    assert not os.path.islink(temp_dir / '.bash_aliases')
    assert not os.path.exists(temp_dir / 'bash' / '.bash_aliases.1')

    entries = [DotyEntry(entry) for entry in new_file]

    compare_lock_yaml()
    assert all([os.path.exists(e.dst) for e in entries])

    assert not os.path.islink(temp_dir / '.bashrc')
    assert not os.path.islink(temp_dir / '.zshrc')
    assert os.path.islink(temp_dir / '.zshrc_unique')
    assert os.readlink(temp_dir / '.zshrc_unique') == str(temp_dir / 'dotfiles' / '.zshrc')
    assert not os.path.exists(temp_dir / '.bash_aliases.original')
    assert os.path.islink(temp_dir / '.bash_aliases')
    assert os.readlink(temp_dir / '.bash_aliases') == str(temp_dir / 'bash' / '.bash_aliases.1')
    assert os.path.exists(temp_dir / 'bash' / '.bash_aliases.1')

    # Testing an edge case to make sure that the "linked" attribute is updated appropriately
    # with open(lock_file) as f:
    #     new_file = yaml.safe_load(f)
    
    # (temp_dir / '.dot_file_bad').touch()
    # new_file.append({ 'name' : '.dot_file_bad', 'linked': True, 'link_name': '.good_entry0' })

    # assert os.path.exists(temp_dir / '.dot_file_bad')
    # assert os.path.exists(temp_dir / '.good_entry0')
    # assert not os.path.islink(temp_dir / '.good_entry0')

    # with open(lock_file, 'w') as f:
    #     yaml.safe_dump(new_file, f, sort_keys=False)
    
    # compare_lock_yaml()
    # err = capfd.readouterr().err
    # assert 'Error' in err
    # assert not os.path.islink(temp_dir / '.good_entry0')

    # with open(lock_file) as f:
    #     new_file = yaml.safe_load(f)
    
    # entry = [e for e in new_file if e['name'] == '.dot_file_bad'][0]
    # assert entry['linked'] == False