import os
import pytest

@pytest.fixture(scope='module', autouse=True)
def setup(temp_dir):
    os.environ.update({'HOME': str(temp_dir)})

def test_get_user_input():
    pass

def test_exit_on_user_input():
    pass
