#!/usr/bin/env python3
"""Uninstall My-Zsh: remove the files install.py placed and restore the
config it backed up beforehand."""

import argparse
import shutil
import sys
from pathlib import Path

HOME_DIR = Path.home()
BACKUP_ROOT = HOME_DIR / ".local" / "share" / "my-zsh" / "backups"

# The destinations install.py writes to (see install.py's install_targets):
# .zprofile and .zshenv go to $HOME, everything else lands in ~/.config/zsh.
INSTALLED = [
    HOME_DIR / ".zprofile",
    HOME_DIR / ".zshenv",
    HOME_DIR / ".config" / "zsh",
]


def find_backups() -> list:
    if not BACKUP_ROOT.is_dir():
        return []
    return sorted(p for p in BACKUP_ROOT.iterdir() if p.is_dir())


def restore_from(backup: Path) -> None:
    for target in INSTALLED:
        rel = target.relative_to(HOME_DIR)
        saved = backup / rel

        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()

        if saved.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            if saved.is_dir():
                shutil.copytree(saved, target)
            else:
                shutil.copy2(saved, target)
            print(f"Restored {target}")
        else:
            print(f"Removed {target} (it did not exist before installation)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove the My-Zsh config and restore your previous zsh setup."
    )
    parser.add_argument(
        "--list", action="store_true", help="List available backups and exit."
    )
    parser.add_argument(
        "--backup",
        type=Path,
        help="Restore a specific backup directory instead of the latest one.",
    )
    parser.add_argument(
        "--yes", action="store_true", help="Do not ask for confirmation."
    )
    args = parser.parse_args()

    backups = find_backups()

    if args.list:
        if backups:
            for b in backups:
                print(b)
        else:
            print("No backups found.")
        return

    backup = args.backup if args.backup else (backups[-1] if backups else None)
    if backup is None or not backup.is_dir():
        print(
            "No backup found - nothing to restore. "
            "A backup is created automatically the first time install.py runs.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"This removes the current My-Zsh config and restores:\n  {backup}\n")
    if not args.yes:
        answer = input("Continue? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Aborted.")
            return

    restore_from(backup)
    print("\nDone. Fully close and reopen Termux for the change to take effect.")
    print("Note: the Termux font (~/.termux/font.ttf) was left in place.")


if __name__ == "__main__":
    main()
