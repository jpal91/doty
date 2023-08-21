import os
import logging
from argparse import ArgumentParser
from helpers.stream_logger import init_stream_logger

init_stream_logger()
logger = logging.getLogger('doty')

# env_path = os.path.join(os.environ['HOME'], '.config', 'doty', 'dotyrc')
env_path = os.path.join(os.environ['HOME'], 'dotfiles', '.doty_config', 'dotyrc')

if __name__ == "__main__":
    parser = ArgumentParser()
    subparser = parser.add_subparsers(dest='command')
    parser_init = subparser.add_parser('init', help='Initialize doty')
    parser_init.add_argument('-a', help='Alternate home directory', type=str, default='')
    parser_init.add_argument('-q', help='Quiet mode - no output', action='store_true', default=False)

    parser_update = subparser.add_parser('update', help='Update doty lock file', aliases=['up'])
    
    parser_status = subparser.add_parser('status', help='Show status of doty lock or config files', aliases=['st'])
    parser_status.add_argument('-l', help='Show all files that are linked to your Home directory', action='store_const', const=1)
    parser_status.add_argument('-N', help='Show all files that are not linked to your Home directory', action='store_const', const=2)
    parser_status.add_argument('-e', help='Show all files that match the given entry name', type=str, default='')
    parser_status.set_defaults(list_lvl=0)
    parser_status.add_argument('-c', help='See the results from the doty config file instead of the lock file', action='store_const', const=1, dest='list_lvl')
    parser_status.add_argument('-A', help='See results from both the doty config and lock files', action='store_const', const=2, dest='list_lvl')
    parser_status.add_argument('-b', help='Show broken entries from config file', action='store_const', const=3, dest='list_lvl')

    parser_create = subparser.add_parser('create', help='Create a new doty entry', aliases=['c'])
    parser_create.add_argument('-C', help='Add confirmations to the create process', action='store_true', dest='check', default=False)
    parser_create.add_argument('-f', help='No confirmations will be given', action='store_true', dest='force', default=False)

    parser_delete = subparser.add_parser('delete', help='Delete a doty entry', aliases=['d', 'del'])
    
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        exit(0)
    
    if args.command == 'init':
        from init import main as init
        init(alt_home=args.a, quiet=args.q)
        exit(0)

    if not os.path.isfile(env_path):
        logger.error("Doty environment file not found - please use 'doty init' to create it")
        exit(1)
    
    from dotenv import load_dotenv
    load_dotenv(env_path)

    from helpers.file_logger import init_file_logger
    init_file_logger()

    if args.command in ['update', 'up']:
        from update import main as update
        update()
        exit(0)

    if args.command in ['status', 'st']:
        from status import main as status
        status(args)
        exit(0)
    
    if args.command in ['create', 'c']:
        from create import main as create
        create(args.check, args.force)
        exit(0)
    
    if args.command in ['delete', 'd', 'del']:
        from update import main as delete
        delete(delete=True)
        exit(0)
    
    