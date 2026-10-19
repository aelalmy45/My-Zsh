import importlib
import shutil
import subprocess
import sys
from pathlib import Path

HOME_DIR = Path.home()

# ------- History path -------
STATE_HOME = HOME_DIR / ".local" / "state" / "zsh"
# ----------------------------

SOURCE = Path(__file__).resolve().parent
DEST = HOME_DIR / ".config" / "zsh"

# ----------- Font File ---------------
FONT_SRC = SOURCE / "font.ttf"
FONT_DEST = HOME_DIR / ".termux" / "font.ttf"

# ----------- Timeouts (seconds) ------
PIP_TIMEOUT = 120
UPDATE_TIMEOUT = 300
UPGRADE_TIMEOUT = 600
INSTALL_TIMEOUT = 600

TIMEOUT_MSG = "The operation timed out. Check your internet connection and try again."


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


exceptions: dict = {".zshenv": Path.home()}

denylist: list = [
    ".git",
    "plugins",
    "README.md",
    "install.py",
    "install.sh",
    ".gitignore",
    "images",
    "font.ttf",
]


def font_installed() -> bool:
    return FONT_DEST.exists()


def install_font() -> tuple[bool, str]:
    if font_installed():
        return True, "\nFont is already installed.\n"

    if not FONT_SRC.exists():
        return False, "Font file not found next to the script!"

    FONT_DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FONT_SRC, FONT_DEST)

    # Apply the new font in Termux
    try:
        subprocess.run(["termux-reload-settings"], capture_output=True)
    except FileNotFoundError:
        pass

    return True, "\nFont copied successfully.\n"


def ensure_rich_installed() -> tuple[bool, str]:
    try:
        import rich  # noqa: F401

        return True, "Rich is already installed\n"
    except ImportError:
        pass

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "rich"],
            capture_output=True,
            text=True,
            timeout=PIP_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, TIMEOUT_MSG
    if proc.returncode != 0:
        return False, f"Error: \n{proc.stderr}"

    importlib.invalidate_caches()
    return True, "Rich was successfully installed\n"


def update_upgrade() -> tuple[bool, str]:
    try:
        update = subprocess.run(
            ["pkg", "update", "-y"],
            capture_output=True,
            text=True,
            timeout=UPDATE_TIMEOUT,
        )

        if update.returncode == 0:
            upgrade = subprocess.run(
                ["pkg", "upgrade", "-y"],
                capture_output=True,
                text=True,
                timeout=UPGRADE_TIMEOUT,
            )
            if upgrade.returncode == 0:
                return True, f"Running start update and upgrade: \n{upgrade.stdout}"
            else:
                return False, f"Error: \n{upgrade.stderr}"
        else:
            return False, f"Error: \n{update.stderr}"
    except subprocess.TimeoutExpired:
        return False, TIMEOUT_MSG


def copy_files_with_rules(source, dest, exceptions, denylist) -> tuple[bool, str]:
    try:
        dest.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            if item.name in denylist:
                continue

            target_dir = exceptions.get(item.name, dest)
            target = target_dir / item.name

            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)
        return True, "The files were successfully copied to their locations.\n"
    except Exception as err:
        return False, f"Error: {err}"


def install_pkgs(*pkg) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            ["pkg", "install", *pkg, "-y"],
            capture_output=True,
            text=True,
            timeout=INSTALL_TIMEOUT,
        )
        if proc.returncode != 0:
            return False, f"Error: \n{proc.stderr}"

        return True, "The packages have been fully installed.\n"
    except subprocess.TimeoutExpired:
        return False, TIMEOUT_MSG


def check_package(pkgs, console) -> list:
    missing: list = []

    for key, value in pkgs.items():
        pkgs_path = shutil.which(key)

        if not pkgs_path:
            missing.append(value)
            console.print(f"[bold yellow]{key} was not found on this system.[/]\n")
    return missing


def main() -> None:
    print("The process is starting, please wait a moment until it is complete.\n")

    STATE_HOME.mkdir(parents=True, exist_ok=True)

    # ---------- Checking for rich ---------------
    sucs_rich, msg_rich = ensure_rich_installed()
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
        with console.status(
            "[bold green]Installing the packages...[/]", spinner="dots"
        ):
            sucs_pkg, msg_pkg = install_pkgs(*missing)
        if not sucs_pkg:
            console.print(f"[bold red]{msg_pkg}[/]")
            return
        console.print(f"[bold green]{msg_pkg}[/]")

    # ----------- Checking copy font file -----------
    sucs_font, msg_font = install_font()
    if not sucs_font:
        console.print(f"[bold red]{msg_font}[/]")
        return
    console.print(f"[bold green]{msg_font}[/]")


if __name__ == "__main__":
    main()
