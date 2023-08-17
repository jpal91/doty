import os
from argparse import ArgumentParser

env_path = os.path.join(os.environ['HOME'], '.config', 'doty', 'dotyrc')

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
        from init import main as init
        init(True)
        exit(0)

    if not os.path.isfile(env_path):
        print("Doty environment file not found - please use 'doty init' to create it")
        exit(1)
    
    from dotenv import load_dotenv
    load_dotenv(env_path)

    if args.command in ['update', 'up']:
        from update import main as update
        update()
        exit(0)