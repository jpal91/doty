import os
import shutil
import yaml
from helpers.git import last_commit_file
from helpers.utils import load_lock_file, write_lock_file, move_file
from classes.entry import DotyEntry
from classes.logger import DotyLogger
from classes.report import ShortReport

logger = DotyLogger()


def parse_entries(entries: list[dict, str]) -> list[dict]:
    """Since the minimum required value for an entry is a string representing a file name,
    this function will convert the string to a dict.
    """
    parsed_entries = []

    for entry in entries:
        if isinstance(entry, str):
            parsed_entries.append({"name": entry})
        elif isinstance(entry, dict):
            parsed_entries.append(entry)
        else:
            logger.error(f"##bred##Error##end## ##bwhite##Invalid entry: {entry}")

    return parsed_entries


def get_lock_files(doty_lock_path: str) -> tuple[list[dict], list[dict]]:
    """Get the prior and current yaml file"""
    prior_yaml = yaml.safe_load(last_commit_file(".doty_config/doty_lock.yml"))
    current_yaml = load_lock_file(doty_lock_path)

    # Parse new entries
    current_yaml = parse_entries(current_yaml)

    return prior_yaml or [], current_yaml or []


def get_lock_file_diff(
    current_entries: list[DotyEntry], prior_entries: list[DotyEntry]
) -> tuple[list[DotyEntry], list[DotyEntry]]:
    """Get the difference between the current and prior yaml file"""
    diff_current = [item for item in current_entries if item not in prior_entries]
    diff_prior = [item for item in prior_entries if item not in current_entries]

    return diff_current, diff_prior


def handle_prior_lock_changes(
    lock_changes: list[DotyEntry], report: ShortReport = None
) -> None:
    """
    Handles any changes from prior locked entries by undoing the changes.
        If there are any symlinks, these will be unlinked. Then the file in the dotfiles
        directory will be moved back to it's source.
    """
    logger.debug("Handling prior lock changes")

    for entry in lock_changes:
        logger.debug(f"Entry: {entry.name}")

        if entry.linked:
            # Since the file could be symlinked under an alias using link_name, we need to
            #  unlink the file using the link_name
            directory = os.path.split(entry.src)[0]
            link_path = os.path.join(directory, entry.link_name)

            if os.path.islink(link_path):
                logger.debug(f"Unlinking {entry.link_name}")
                os.unlink(link_path)

                if report:
                    report.rm_link(entry.link_name)

        # Verify the file exists in the dotfiles directory
        if not os.path.exists(entry.dst):
            logger.error(
                f"##bred##Error##end## ##bwhite##File {entry.name} - {entry.dst} does not exist. Skipping..."
            )
            continue

        # Verify there is no file or symlink matching src path to prevent overwriting
        if os.path.exists(entry.src) or os.path.islink(entry.src):
            logger.error(
                f"##bred##Error##end## ##bwhite##Moving file {entry.name} to {entry.src} already exists. Skipping..."
            )
            continue

        logger.debug(f"Moving {entry.dst} to {entry.src}")
        shutil.move(entry.dst, entry.src)

        if report:
            report.rm_file(entry.name)


def handle_current_lock_changes(
    lock_changes: list[DotyEntry], report: ShortReport = None
) -> None:
    """Handles changes to the new lock file by creating symlinks for the new entries
    and moving files to the dotfiles directory.
    """
    dotfiles_dir = os.environ["DOTFILES_PATH"]
    logger.debug("Handling current lock changes")

    for entry in lock_changes:
        logger.debug(f"Entry: {entry.name}")

        # Verify the file exists at src and is not a symlink
        if not os.path.exists(entry.src) or os.path.islink(entry.src):
            logger.error(
                f"##bred##Error##end## ##bwhite##File {entry.name} - {entry.src} does not exist. Skipping..."
            )
            continue

        # Verify dst does not exist
        if os.path.exists(entry.dst):
            logger.error(
                f"##bred##Error##end## ##bwhite##File {entry.name} - {entry.dst} already exists. Skipping..."
            )
            continue

        # Verify destination is in the dotfiles directory
        if not entry.dst.startswith(dotfiles_dir):
            logger.error(
                f"##bred##Error##end## ##bwhite##File {entry.name} - {entry.dst} is not in the dotfiles directory. Skipping..."
            )
            continue

        # Move the file to the dotfiles directory
        # Using special move function to create directories if needed
        logger.debug(f"Moving {entry.src} to {entry.dst}")
        move_file(entry.src, entry.dst)

        if report:
            report.add_file(entry.name)

        # Handle linking
        if entry.linked:
            linked_name = os.path.join(os.path.split(entry.src)[0], entry.link_name)

            # Verify there is no file or symlink matching link_name path to prevent overwriting
            if os.path.exists(linked_name) or os.path.islink(linked_name):
                logger.error(
                    f"##bred##Error##end## ##bwhite##File {entry.name} - {linked_name} already exists. Skipping..."
                )
                entry.linked = False
                continue

            logger.debug(f"Linking {entry.dst} to {linked_name}")
            os.symlink(entry.dst, linked_name)

            if report:
                report.add_link(entry.link_name)


def compare_lock_yaml(report: bool = True) -> ShortReport:
    """Compare the doty_lock.yml file with the prior yml file"""
    doty_lock_path = os.path.join(
        os.environ["DOTFILES_PATH"], ".doty_config", "doty_lock.yml"
    )
    prior_yaml, current_yaml = get_lock_files(doty_lock_path)

    if report:
        report = ShortReport()
    else:
        report = None

    # Converts yaml into list of DotyEntry objects
    prior_entries = [DotyEntry(entry) for entry in prior_yaml]
    current_entries = [DotyEntry(entry) for entry in current_yaml]

    # Get the difference between the current and prior yaml file
    diff_current, diff_prior = get_lock_file_diff(current_entries, prior_entries)

    # Handle any changes from prior locked entries
    handle_prior_lock_changes(diff_prior, report=report)

    # Handle any changes to the new lock file
    handle_current_lock_changes(diff_current, report=report)

    # Write current entries to lock file
    new_yaml = [entry.dict for entry in current_entries]
    write_lock_file(new_yaml, doty_lock_path)

    return report
