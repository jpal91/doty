import os
import pytest
from doty.classes.report import ReportItem
from doty.classes.entry import DotyEntry

@pytest.fixture(scope="module", autouse=True)
def setup(temp_dir):
    os.environ.update(
        {"HOME": str(temp_dir), "DOTFILES_PATH": str(temp_dir / "dotfiles")}
    )

@pytest.fixture
def report_item():
    return ReportItem()

@pytest.fixture
def entry_a():
    return DotyEntry({ 'name': 'test' })

@pytest.fixture
def entry_b():
    return DotyEntry({ 'name': 'test' })

def test_add(report_item, entry_b):
    assert report_item.entry_a is None
    assert report_item.entry_b is None
    report_item.add(entry_b)
    assert report_item.entry_a is None
    assert report_item.entry_b == entry_b

def test_rm(report_item, entry_a):
    assert report_item.entry_a is None
    assert report_item.entry_b is None
    report_item.rm(entry_a)
    assert report_item.entry_a == entry_a
    assert report_item.entry_b is None

def test_is_update(report_item, entry_a, entry_b):
    print(report_item.entry_a, report_item.entry_b)
    assert report_item.is_update is False
    report_item.add(entry_b)
    assert report_item.is_update is False
    report_item.rm(entry_a)
    assert report_item.is_update is True

def test_is_add(report_item, entry_b):
    assert report_item.is_add is False
    report_item.add(entry_b)
    assert report_item.is_add is True

def test_is_rm(report_item, entry_a):
    assert report_item.is_rm is False
    report_item.rm(entry_a)
    assert report_item.is_rm is True

def test_link_report(entry_a, entry_b):
    report_item_is_update = ReportItem()
    report_item_is_update.add(entry_b)
    report_item_is_update.rm(entry_a)
    assert report_item_is_update.is_update is True
    report = report_item_is_update.link_report
    assert '##bblue##Updated ##bwhite##link' in report
    assert entry_b.name in report
    assert entry_a.linked_path in report
    assert entry_b.dst in report

    report_item_is_update = ReportItem()
    report_item_is_update.add(entry_b)
    entry_a.linked = False
    report_item_is_update.rm(entry_a)
    assert report_item_is_update.is_update is True
    report = report_item_is_update.link_report
    assert '##bgreen##Updated ##bwhite##link' in report
    assert entry_b.name in report
    assert entry_b.linked_path in report
    assert entry_b.dst in report

    report_item_is_update = ReportItem()
    entry_a.linked = True
    entry_b.linked = False
    report_item_is_update.add(entry_b)
    report_item_is_update.rm(entry_a)
    assert report_item_is_update.is_update is True
    report = report_item_is_update.link_report
    assert '##bred##Removed ##bwhite##link' in report
    assert entry_a.linked_path in report

    entry_a.linked = True
    entry_b.linked = True

    report_item_is_add = ReportItem()
    report_item_is_add.add(entry_b)
    assert report_item_is_add.is_update is False
    assert report_item_is_add.is_add is True
    report = report_item_is_add.link_report
    assert '##bgreen##Added ##bwhite##link' in report
    assert entry_b.name in report
    assert entry_b.linked_path in report
    assert entry_b.dst in report

    report_item_is_rm = ReportItem()
    report_item_is_rm.rm(entry_a)
    assert report_item_is_rm.is_update is False
    assert report_item_is_rm.is_rm is True
    report = report_item_is_rm.link_report
    assert '##bred##Removed ##bwhite##link' in report
    assert entry_a.name in report
    assert entry_a.linked_path in report
    assert entry_a.dst in report

def test_file_report(temp_dir, entry_a, entry_b):
    report_item_is_update = ReportItem()
    entry_b.dst = str(temp_dir / 'dotfiles' / 'test' / 'test')
    report_item_is_update.add(entry_b)
    report_item_is_update.rm(entry_a)
    assert report_item_is_update.is_update is True
    assert entry_b.dst != entry_a.dst
    report = report_item_is_update.file_report
    assert '##bblue##Updated ##bwhite##dotfile path' in report
    assert entry_b.name in report
    assert entry_a.dst in report
    assert entry_b.dst in report

    report_item_is_update = ReportItem()
    entry_b.dst = str(temp_dir / 'dotfiles' / 'test')
    entry_b.link_name = 'test1'
    report_item_is_update.add(entry_b)
    report_item_is_update.rm(entry_a)
    assert entry_b.dst == entry_a.dst
    assert entry_b.link_name != entry_a.link_name
    report = report_item_is_update.file_report
    assert '##bblue##Updated ##bwhite##dotfile link name' in report
    assert entry_b.name in report
    assert entry_a.link_name in report
    assert entry_b.link_name in report

    report_item_is_update = ReportItem()
    entry_b.link_name = 'test'
    report_item_is_update.add(entry_b)
    report_item_is_update.rm(entry_a)
    assert entry_b.dst == entry_a.dst
    assert entry_b.link_name == entry_a.link_name
    report = report_item_is_update.file_report
    assert report == ''

    report_item_is_add = ReportItem()
    report_item_is_add.add(entry_b)
    assert report_item_is_add.is_update is False
    assert report_item_is_add.is_add is True
    report = report_item_is_add.file_report
    assert '##bgreen##Added ##bwhite##file' in report
    assert entry_b.name in report
    assert entry_b.src in report
    assert entry_b.dst in report

    report_item_is_rm = ReportItem()
    report_item_is_rm.rm(entry_a)
    assert report_item_is_rm.is_update is False
    assert report_item_is_rm.is_rm is True
    report = report_item_is_rm.file_report
    assert '##bred##Removed ##bwhite##file' in report
    assert entry_a.name in report
    assert entry_a.src in report
    assert entry_a.dst in report
    
