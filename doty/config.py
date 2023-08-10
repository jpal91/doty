import os

def config(home_dir: str):
    
    # Checks if dotfiles directory exists
    dotfiles_dir = os.path.join(home_dir, "dotfiles")
    if not os.path.isdir(dotfiles_dir):
        print("Dotfiles directory does not exist. Creating...")
        os.mkdir(dotfiles_dir)
    
    # Checks if dotfiles .config file exists
    dotfiles_config = os.path.join(dotfiles_dir, ".config")
    if not os.path.isfile(dotfiles_config):
        print("Dotfiles config file does not exist. Creating...")
        with open(dotfiles_config, "w") as f:
            f.write("")
    