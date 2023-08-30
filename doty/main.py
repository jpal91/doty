import os
from helpers.args import main_args
from update import update
from add import add

if __name__ == '__main__':
    arg_parser = main_args()
    args = arg_parser.parse_args()
    
    if not args.command:
        arg_parser.print_help()
        exit(0)
    
    if args.command in ['update', 'up']:
        update(commit=not args.no_commit, quiet=args.quiet, dry_run=args.dry_run)
    
    if args.command in ['add', 'a']:
        add(args.entry_name, args.src, args.dst, force=args.force, no_git=args.no_git, no_link=args.no_link)