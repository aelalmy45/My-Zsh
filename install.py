import shutil
import subprocess
from pathlib import Path


print("The process is starting, please wait a moment until it is complete.\n")

SOURCE = Path(__file__).resolve().parent
DEST = Path.home() / ".config" / "zsh"
DEST.mkdir(parents=True, exist_ok=True)

missing: list = []

pkgs: dict = {
        "zsh": "zsh",
        "git": "git",
        "eza": "eza",
        "rg": "ripgrep",
        "fd": "fd",
        "bat": "bat",
        "zoxide": "zoxide",
        "fzf": "fzf",
        "lf": "lf",
        "nvim": "neovim",
        "starship": "starship",
    }


exceptions: dict = {
        ".zprofile": Path.home()
        }

denylist: list = [
        ".git",
        "plugins",
        "README.md", 
        "install.py",
        "install.sh", 
        ".gitignore", 
        "images",
        ]


def update_upgrade() -> str:
    update = subprocess.run([
        "pkg",
        "update",
        "-y"
        ], capture_output=True, text=True)

    if update.returncode == 0:
        upgrade = subprocess.run([
            "pkg",
            "upgrade",
            "-y"
            ], capture_output=True, text=True)
        if upgrade.returncode == 0:
            return f"Running start update and upgrade: \n{upgrade.stdout}"
        else:
            return f"Error: \n{upgrade.stderr}"
    else:
        return f"Error: \n{update.stderr}"


def copy_files_with_rules(
        SOURCE, 
        DEST, 
        exceptions, 
        denylist
        ) -> None:
    for item in SOURCE.iterdir():
        if item.name in denylist:
            pass
        elif item.name in exceptions:
            dest_path = exceptions[item.name] / item.name
            shutil.copy2(item, dest_path)
        else:
            dest_path = DEST / item.name
            shutil.copy2(item, dest_path)


def install_pkgs(*pkg) -> str:
    proc = subprocess.run([
        "pkg",
        "install",
        *pkg,
        "-y"
        ], capture_output=True, text=True)

    if proc.returncode != 0:
        return f"Error: \n{proc.stderr}"

    return f"Running start process: \n{proc.stdout}"


def check_package(pkgs) -> None:
    global missing

    for key, value in pkgs.items():
        pkgs_path = shutil.which(key)

        if not pkgs_path:
            missing.append(value)
            print(f"{key} was not found on this system.\n")


def main() -> None:
    print(update_upgrade())
    copy_files_with_rules(SOURCE, DEST, exceptions, denylist)
    check_package(pkgs)
    if missing:
        print(install_pkgs(*missing))


if __name__ == "__main__":
    main()
