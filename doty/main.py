import os
import subprocess
from helpers.args import main_args
from update import update
from add import add
from remove import remove

if __name__ == '__main__':
    arg_parser = main_args()
    args = arg_parser.parse_args()
    
    if not args.command:
        arg_parser.print_help()
        exit(0)
    
    if args.command in ['update', 'up']:
        update(commit=not args.no_commit, quiet=args.quiet, dry_run=args.dry_run)
    
    if args.command in ['add', 'a']:
        add(args.entry_name, args.src, args.dst, args.link_name, force=args.force, no_git=args.no_git, no_link=args.no_link)
    
    if args.command in ['remove', 'rm']:
        remove(args.name, link_only=args.link, no_git=args.no_git, force=args.force)
    
    if args.command in ['edit', 'e']:
        if args.lock:
            lock_path = os.path.join(os.environ['DOTFILES_PATH'], '.doty_config', 'doty_lock.yml')
            process = subprocess.run(['nano', lock_path])
            exit(process.returncode)