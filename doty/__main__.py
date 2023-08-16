import os
from argparse import ArgumentParser
from dotenv import load_dotenv
load_dotenv()
# from update import main as update

DOTDIR = os.environ['DOTY_DIR']

def dot_exists() -> bool:
    if not DOTDIR:
        return False
    
    if not os.path.exists(DOTDIR):
        return False
    
    lock, cfg = os.path.join(DOTDIR, 'doty_lock.yml'), os.path.join(DOTDIR, 'dotycfg.yml')

    if not os.path.exists(lock) or not os.path.exists(cfg):
        return False
    
    return True

if __name__ == "__main__":
    parser = ArgumentParser()
    subparser = parser.add_subparsers(dest='command')
    parser_init = subparser.add_parser('init', help='Initialize doty')
    parser_update = subparser.add_parser('update', help='Update doty lock file', aliases=['up'])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        exit(0)
    
    if args.command == 'init':
        pass

    if not dot_exists():
        print('Doty is not properly configured, please use doty init to set up')
        exit(1)

    # update()