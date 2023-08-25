from argparse import ArgumentParser, Namespace

def init_args() -> Namespace:
    parser = ArgumentParser(description='A tool for managing dotfiles')
    # parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')
    parser.add_argument('-q', '--quiet', action='store_true', help='suppress output', dest='quiet', default=False)
    parser.add_argument('-t', '--temp', action='store_true', help='Use a temporary directory, defaults to /tmp/dotytmp', dest='temp', default=False)

    return parser.parse_args()