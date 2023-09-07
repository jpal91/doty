import os
from pathlib import Path
import pytest
from doty.classes.entry import DotyEntry

@pytest.fixture(scope="module", autouse=True)
def setup(temp_dir, dummy_files):
    os.environ.update(
        {"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles")}
    )

def test_eq(temp_dir):
    entry1 = { 'name': '.bashrc' }
    entry2 = { 
        'name': '.bashrc', 
        'src': str(temp_dir / '.bashrc'), 
        'dst': str(temp_dir / 'dotfiles' / '.bashrc'),
        'linked': True,
        'link_name': '.bashrc'
    }
    entry3 = { 'name': '.wshrc' }
    entry4 = { 
        'name': '.wshrc', 
        'src': str(temp_dir / '.wshrc'), 
        'dst': str(temp_dir / 'dotfiles' / '.wshrc'),
        'linked': True,
        'link_name': '.wshrc'
    }

    assert DotyEntry(entry1) == DotyEntry(entry1)
    assert DotyEntry(entry2) == DotyEntry(entry2)
    assert DotyEntry(entry1) == DotyEntry(entry2)
    assert DotyEntry(entry3) == DotyEntry(entry4)
    assert DotyEntry(entry1) != DotyEntry(entry3)
    assert DotyEntry(entry1) != DotyEntry(entry4)

def test_dict(temp_dir):
    entry = { 
        'name': '.bashrc', 
        'src': str(temp_dir / '.bashrc'), 
        'dst': str(temp_dir / 'dotfiles' / '.bashrc'),
        'linked': True,
        'link_name': '.bashrc'
    }
    doty_entry1 = DotyEntry({'name': '.bashrc'})
    doty_entry2 = DotyEntry(entry)

    assert doty_entry1.dict == entry
    assert doty_entry2.dict == entry
    del entry['name']
    assert doty_entry1.dict != entry

def test_linked_path(temp_dir):
    entry1 = DotyEntry({'name': '.bashrc'})
    entry2 = DotyEntry({'name': '.bashrc', 'link_name': '.bashrc.1'})
    entry3 = DotyEntry({'name': '.bashrc', 'src': '/home/user/.bashrc', 'link_name': '.bashrc.1'})

    assert entry1.linked_path == str(temp_dir / '.bashrc')
    assert entry2.linked_path == str(temp_dir  / '.bashrc.1')
    assert entry3.linked_path == '/home/user/.bashrc.1'

@pytest.fixture
def tmp(temp_dir):
    return str(temp_dir)

@pytest.mark.parametrize(
    'input,expected',
    [
        (
            {'nothing': 'nothing'},
            {'name': '', 'src': '', 'dst': '', 'linked': True, 'link_name': ''}
        ),
        (
            {'src': 'temp_dir/.bashrc'},
            {}
        ),
        (
            {'name': '.bashrc'},
            {}
        ),
        (
            {'name': '.bashrc', 'src': 'temp_dir/bash/.bashrc'}, # Dual test, no dst, no default dir in src
            {'src': 'temp_dir/bash/.bashrc'}
        ),
        (
            {'name': '.bashrc', 'src': 'temp_dir/.bashrc', 'dst': 'bash/.bashrc'}, # dst present and not absolute
            {'dst': 'temp_dir/dotfiles/bash/.bashrc'}
        ),
        (
            {'name': '.bashrc', 'link_name': '.bashrc.1'}, # link_name present
            {'link_name': '.bashrc.1'}
        ),
        (
            {'name': '.bashrc', 'linked': False}, # linked present
            {'linked': False}
        )
    ]
)
def test_extrapolate(temp_dir, input, expected):
    expected_dict = {
        'name': '.bashrc',
        'src': str(temp_dir / '.bashrc'),
        'dst': str(temp_dir / 'dotfiles' / '.bashrc'),
        'linked': True,
        'link_name': '.bashrc'
    }

    if 'src' in input:
        input['src'] = input['src'].replace('temp_dir', str(temp_dir))
    elif 'dst' in input:
        input['dst'] = input['dst'].replace('temp_dir', str(temp_dir))
    
    if 'src' in expected:
        expected['src'] = expected['src'].replace('temp_dir', str(temp_dir))
    elif 'dst' in expected:
        expected['dst'] = expected['dst'].replace('temp_dir', str(temp_dir))
    
    expected = { **expected_dict, **expected }

    entry = DotyEntry(input)

    assert entry.dict == expected