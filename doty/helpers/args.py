from argparse import ArgumentParser, Namespace

def init_args() -> Namespace:
    parser = ArgumentParser(description='Tool to initialize Doty, create a repo, and add all needed files')
    # parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('-q', '--quiet', action='store_true', help='suppress output', dest='quiet', default=False)
    parser.add_argument('-t', '--temp', action='store_true', help='Use a temporary directory, defaults to /tmp/dotytmp', dest='temp', default=False)

    return parser.parse_args()

def main_args() -> Namespace:
    """Arguments for the main function"""
    parser = ArgumentParser()
    subparser = parser.add_subparsers(dest='command')

    parser_update = subparser.add_parser('update', help='Update doty lock file', aliases=['up'])
    
    # parser_status = subparser.add_parser('status', help='Show status of doty lock or config files', aliases=['st'])
    # parser_status.add_argument('-l', help='Show all files that are linked to your Home directory', action='store_const', const=1)
    # parser_status.add_argument('-N', help='Show all files that are not linked to your Home directory', action='store_const', const=2)
    # parser_status.add_argument('-e', help='Show all files that match the given entry name', type=str, default='')
    # parser_status.set_defaults(list_lvl=0)
    # parser_status.add_argument('-c', help='See the results from the doty config file instead of the lock file', action='store_const', const=1, dest='list_lvl')
    # parser_status.add_argument('-A', help='See results from both the doty config and lock files', action='store_const', const=2, dest='list_lvl')
    # parser_status.add_argument('-b', help='Show broken entries from config file', action='store_const', const=3, dest='list_lvl')

    # parser_create = subparser.add_parser('create', help='Create a new doty entry', aliases=['c'])
    # parser_create.add_argument('-C', help='Add confirmations to the create process', action='store_true', dest='check', default=False)
    # parser_create.add_argument('-f', help='No confirmations will be given', action='store_true', dest='force', default=False)
    parser_add = subparser.add_parser('add', help='Add a new doty entry', aliases=['a'])
    # parser_add.add_argument('-C', help='Add confirmations to the create process', action='store_true', dest='check', default=False)
    parser_add.add_argument('-e', help='Entry name', type=str, default='', dest='entry_name')
    parser_add.add_argument('-s', help='Source file', type=str, default='', dest='src')
    parser_add.add_argument('-d', help='Destination file', type=str, default='', dest='dst')
    parser_add.add_argument('--no-git', help='Do not add the entry to the git repo', action='store_true', dest='no_git', default=False)
    parser_add.add_argument('--no-link', help='Do not link the entry to the home directory', action='store_true', dest='no_link', default=False)

    # parser_delete = subparser.add_parser('delete', help='Delete a doty entry', aliases=['d', 'del'])
    
    args = parser.parse_args()
