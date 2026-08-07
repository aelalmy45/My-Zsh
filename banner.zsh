# =========================================================
# Terminal Banner
# =========================================================

banner() {
  printf '\033[38;2;0;215;255m'
  command cat "$HOME/.config/zsh/banner"
  printf '\033[0m'
}

banner
