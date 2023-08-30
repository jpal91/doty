import os

def find_all_dotfiles() -> list:
    """Find all dotfiles in the user's home directory."""
    dot_dir = os.path.join(os.environ['HOME'], 'dotfiles')
    dotfiles = []

    for root, dirs, files in os.walk(dot_dir):
        # Skips .doty_config
        if '.doty_config' in dirs:
            dirs.remove('.doty_config')
        if '.git' in dirs:
            dirs.remove('.git')

        for file in files:
            if file == '.gitignore':
                continue
            dotfiles.append(os.path.join(root, file))
    return dotfiles

def find_all_links(dotfiles: list) -> list:
    """Find all links in the user's home directory."""
    links = []
    for dotfile in dotfiles:
        base = os.path.basename(dotfile)
        home_path = os.path.join(os.environ['HOME'], base)
        if os.path.islink(home_path):
            links.append(home_path)
    return links

def get_doty_ignore() -> list:
    """Get the contents of .dotyignore"""
    doty_ignore = os.path.join(os.environ['HOME'], 'dotfiles', '.doty_config', '.dotyignore')
    if os.path.isfile(doty_ignore):
        with open(doty_ignore, 'r') as f:
            items = [ item.strip() for item in f.readlines() if not item.startswith('#') ]
            return items
    return []

def discover() -> list:
    """Find any files in the dotfiles directory which are not linked yet"""
    doty_ignore = get_doty_ignore()
    dotfiles = find_all_dotfiles()
    links = find_all_links(dotfiles)
    
    base_links = [os.path.basename(link) for link in links]
    new_link = [dotfile for dotfile in dotfiles if os.path.basename(dotfile) not in base_links and os.path.basename(dotfile) not in doty_ignore]
    unlink = [ignored for ignored in doty_ignore if ignored in base_links]

    return new_link, unlink