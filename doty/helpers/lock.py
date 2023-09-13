import os
import yaml
from helpers.git import last_commit_file
from helpers.utils import load_lock_file, write_lock_file, move_file, move_out
from classes.entry import DotyEntry
from classes.logger import DotyLogger
from classes.report import ShortReport2 as ShortReport

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
    try:
        prior_yaml = yaml.safe_load(last_commit_file(".doty_config/doty_lock.yml"))
        current_yaml = load_lock_file(doty_lock_path)
    except yaml.YAMLError:
        logger.critical(
            "##bred##YAML file is invalid. Please check the file and try again."
        )
        exit(1)

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


def check_for_mismatch(
    diff_current: list[DotyEntry], current_entries: list[DotyEntry]
) -> list[DotyEntry]:
    """Checks for entries that haven't changed from prior commit, but still may not be correct"""

    for entry in current_entries:
        if entry in diff_current:
            continue

        if not os.path.exists(entry.dst):
            logger.warning(
                f"##bblue##Entry##end## ##bwhite##{entry.name}##bblue## not in correct dst - adding to queue"
            )
            diff_current.append(entry)
            continue

        link_path = os.path.join(os.environ["HOME"], entry.link_name)

        if entry.linked and not os.path.islink(link_path):
            logger.warning(
                f"##bblue##Entry##end## ##bwhite##{entry.name}##bblue## not linked - adding to queue"
            )
            diff_current.append(entry)
            continue

        if not entry.linked and os.path.islink(link_path):
            logger.warning(
                f"##bblue##Entry##end## ##bwhite##{entry.name}##bblue## linked, but should not be - adding to queue"
            )
            diff_current.append(entry)
            continue

    return diff_current

def fix_links(current_entries: list[DotyEntry], report: ShortReport) -> ShortReport:
    """Checks for entries that haven't changed from prior commit, but still may not be correct"""

    for entry in current_entries:
        link_path = os.path.join(os.environ["HOME"], entry.link_name)

        if entry.linked and not os.path.exists(link_path):
            os.symlink(entry.dst, link_path)
            report.add_link(entry.link_name, entry)
            continue

        if not entry.linked and os.path.islink(link_path):
            os.unlink(link_path)
            report.rm_link(entry.link_name, entry)
            continue

    return report


def handle_prior_lock_changes(
    lock_changes: list[DotyEntry], report: ShortReport, dry_run: bool = False
) -> None:
    """
    Handles any changes from prior locked entries by undoing the changes.
        If there are any symlinks, these will be unlinked. Then the file in the dotfiles
        directory will be moved back to it's source.
    """
    logger.debug("Handling prior lock changes")

    for entry in lock_changes:
        logger.debug(f"Entry: {entry.name}")
        directory = os.path.split(entry.src)[0]
        link_path = os.path.join(directory, entry.link_name)

        if entry.linked:
            # Since the file could be symlinked under an alias using link_name, we need to
            #  unlink the file using the link_name

            # link_path = os.path.join(directory, entry.link_name)

            if os.path.islink(link_path):
                logger.debug(f"Unlinking {entry.link_name}")
                if not dry_run:
                    os.unlink(link_path)

                report.rm_link(entry.link_name, entry)

        # Verify the file exists in the dotfiles directory
        if not os.path.exists(entry.dst):
            logger.error(
                f"##bred##Error##end## ##bwhite##File {entry.name} - {entry.dst} does not exist. Skipping..."
            )
            continue

        # Verify there is no file or symlink matching src path to prevent overwriting
        # Does not need to check on dry_run because no files/links will be changed
        if not dry_run and (os.path.exists(entry.src) or os.path.islink(link_path)):
            logger.error(
                f"##bred##Error##end## ##bwhite##Moving file {entry.name} to {entry.src} already exists. Skipping..."
            )
            continue

        logger.debug(f"Removing {entry.dst} to {entry.src}")
        # shutil.move(entry.dst, entry.src)
        if not dry_run:
            move_out(entry.dst, entry.src)

        report.rm_file(entry.name, entry)


def handle_current_lock_changes(
    lock_changes: list[DotyEntry], report: ShortReport, dry_run: bool = False
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
        logger.debug(f"Moving{entry.src} to {entry.dst}")
        if not dry_run:
            move_file(entry.src, entry.dst)

        report.add_file(entry.name, entry)

        # Handle linking
        if entry.linked:
            linked_name = os.path.join(os.path.split(entry.src)[0], entry.link_name)

            # Verify there is no file or symlink matching link_name path to prevent overwriting
            # Does not need to check on dry_run because no files/links will be changed
            if not dry_run and (
                os.path.exists(linked_name) or os.path.islink(linked_name)
            ):
                logger.error(
                    f"##bred##Error##end## ##bwhite##File {entry.name} - {linked_name} already exists. Skipping..."
                )
                entry.linked = False
                continue

            logger.debug(f"Linking {entry.dst} to {linked_name}")
            if not dry_run:
                os.symlink(entry.dst, linked_name)

            report.add_link(entry.link_name, entry)


def compare_lock_yaml(
    dry_run: bool = False,
    doty_lock_path: str = None,
) -> ShortReport:
    """Compare the doty_lock.yml file with the prior yml file"""

    if not doty_lock_path:
        doty_lock_path = os.path.join(
            os.environ["DOTFILES_PATH"], ".doty_config", "doty_lock.yml"
        )

    prior_yaml, current_yaml = get_lock_files(doty_lock_path)

    report = ShortReport()

    # Converts yaml into list of DotyEntry objects
    prior_entries = [DotyEntry(entry) for entry in prior_yaml]
    current_entries = [DotyEntry(entry) for entry in current_yaml]

    # Get the difference between the current and prior yaml file
    diff_current, diff_prior = get_lock_file_diff(current_entries, prior_entries)

    # Check for mismatched entries
    diff_current = check_for_mismatch(diff_current, current_entries)

    # Handle any changes from prior locked entries
    handle_prior_lock_changes(diff_prior, report, dry_run=dry_run)

    # Handle any changes to the new lock file
    handle_current_lock_changes(diff_current, report, dry_run=dry_run)

    # Fix any remaining broken symlinks
    if not dry_run:
        report = fix_links(current_entries, report)

    # Write current entries to lock file
    new_yaml = [entry.dict for entry in current_entries]

    write_lock_file(new_yaml, doty_lock_path)

    return report
