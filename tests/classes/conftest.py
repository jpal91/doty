import pytest
from dotenv import load_dotenv

@pytest.fixture(autouse=True, scope='session')
def load_env(temp_dir):
    load_dotenv(temp_dir / '.config' / 'doty' / 'dotyrc')
