# =========================================================
# Terminal Banner
# =========================================================

hex_color() {
  local hex="${1#\#}"

  local r=$((16#${hex[1,2]}))
  local g=$((16#${hex[3,4]}))
  local b=$((16#${hex[5,6]}))

  printf '\033[38;2;%d;%d;%dm' "$r" "$g" "$b"
}

banner() {
  printf '%s' "$(hex_color '#156AFF')"
  command cat "$HOME/.config/zsh/banner"
  printf '\033[0m'
}

banner
