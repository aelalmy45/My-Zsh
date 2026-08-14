import shutil
import subprocess
from pathlib import Path


print("The process is starting, please wait a moment until it is complete.\n")

SOURCE = Path(__file__).resolve().parent
DEST = Path.home() / ".config" / "zsh"


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


def ensure_rich_installed() -> tuple[bool, str]:
    try:
        proc = subprocess.run([
            "pip",
            "install",
            "rich"
            ], capture_output=True, text=True, timeout=50)
    except subprocess.TimeoutExpired:
        return False, "Make sure you are connected to the internet."
    if proc.returncode != 0:
        return False, f"Error: \n{proc.stderr}"

    return True, "Rich was successfully installed\n"


def update_upgrade() -> tuple[bool, str]:
    try:
        update = subprocess.run([
            "pkg",
            "update",
            "-y"
            ], capture_output=True, text=True, timeout=60)

        if update.returncode == 0:
            upgrade = subprocess.run([
                "pkg",
                "upgrade",
                "-y"
                ], capture_output=True, text=True, timeout=60)
            if upgrade.returncode == 0:
                return True, f"Running start update and upgrade: \n{upgrade.stdout}"
            else:
                return False, f"Error: \n{upgrade.stderr}"
        else:
            return False, f"Error: \n{update.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Make sure you are connected to the internet."


def copy_files_with_rules(
        SOURCE,
        DEST,
        exceptions, 
        denylist
        ) -> tuple[bool, str]:
    try:

        DEST.mkdir(parents=True, exist_ok=True)
        for item in SOURCE.iterdir():
            if item.name in denylist:
                pass
            elif item.name in exceptions:
                dest_path = exceptions[item.name] / item.name
                shutil.copy2(item, dest_path)
            else:
                dest_path = DEST / item.name
                shutil.copy2(item, dest_path)
        return True, "The files were successfully copied to their locations.\n"
    except Exception as err:
        return False, f"Error: {err}"


def install_pkgs(*pkg) -> tuple[bool, str]:
    try:
        proc = subprocess.run([
            "pkg",
            "install",
            *pkg,
            "-y"
            ], capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return False, f"Error: \n{proc.stderr}"

        return True, "The packages have been fully installed.\n"
    except subprocess.TimeoutExpired:
        return False, "Make sure you are connected to the internet."


def check_package(pkgs, console) -> list:
    missing: list = []

    for key, value in pkgs.items():
        pkgs_path = shutil.which(key)

        if not pkgs_path:
            missing.append(value)
            console.print(f"[bold yellow]{key} was not found on this system.[/]\n")
    return missing


def main() -> None:
    # ---------- Checking for rich ---------------
    sucs_rich , msg_rich = ensure_rich_installed()
    if not sucs_rich:
        print(msg_rich)
        return
    # ---------------- Rich ----------------------
    from rich.console import Console
    console = Console()
    console.print(f"[bold green]{msg_rich}[/]")

    # ----- Checking for update upgrade ----------
    with console.status("[bold green]System update in progress...[/]", spinner="dots"):
        sucs_up, msg_up = update_upgrade()
    if not sucs_up:
        console.print(f"[bold red]{msg_up}[/]")
        return
    console.print(f"[bold green]{msg_up}[/]")

    missing = check_package(pkgs, console)

    # ----------- Checking copy files ---------------
    sucs_cp, msg_cp = copy_files_with_rules(SOURCE, DEST, exceptions, denylist)
    if not sucs_cp:
        console.print(f"[bold red]{msg_cp}[/]")
        return
    console.print(f"[bold green]{msg_cp}[/]")

    # ----------- Checking install pkgs -------------
    if missing:
        with console.status("[bold green]Installing the packages...[/]", spinner="dots"):
            sucs_pkg, msg_pkg = install_pkgs(*missing)
        if not sucs_pkg:
            console.print(f"[bold red]{msg_pkg}[/]")
            return
        console.print(f"[bold green]{msg_pkg}[/]")


if __name__ == "__main__":
    main()
