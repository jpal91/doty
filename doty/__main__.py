import os
import sys
import runpy
from dotenv import load_dotenv

if __name__ == '__main__':
    env_path = os.path.join(os.environ['HOME'], 'dotfiles', '.doty_config', 'dotyrc')

    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        del sys.argv[1]
        runpy.run_module('init', run_name='__main__')
    elif not env_path:
        runpy.run_module('init', run_name='__main__')
    else:
        load_dotenv(env_path)
        runpy.run_module('main', run_name='__main__')
