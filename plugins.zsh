# =========================================================
# Plugins (pinned versions)
# =========================================================
# Every plugin is pinned to a fixed upstream tag, so each install gets
# exactly the same code instead of whatever "latest" happens to be.
# To upgrade a plugin: bump its tag below, run `zplugin-update`, and
# restart the shell.

ZPLUGINDIR="${ZDOTDIR:-$HOME/.config/zsh}/plugins"

# owner repo pinned-tag (loading order: syntax highlighting last)
ZPLUGIN_LIST=(
  "zsh-users zsh-autosuggestions v0.7.1"
  "zsh-users zsh-history-substring-search v1.1.0"
  "jeffreytse zsh-vi-mode v0.12.0"
  "zdharma-continuum fast-syntax-highlighting v1.56"
)

_zplugin_load() {
  local plugin_path="${ZPLUGINDIR}/${2}"
  if [[ ! -d "$plugin_path" ]]; then
    mkdir -p "$ZPLUGINDIR"
    echo "Installing ${2}@${3}..."
    git clone --depth=1 --branch "$3" "https://github.com/${1}/${2}" "$plugin_path" \
      || { echo "ERROR: failed to install ${2}" >&2; return 1; }
  fi
  source "${plugin_path}/${2}.plugin.zsh"
}

zplugin-update() {
  echo "Plugins are pinned in plugins.zsh - reinstalling the pinned versions."
  if [[ -d "$ZPLUGINDIR" ]]; then
    command rm -rf "$ZPLUGINDIR"
  fi
  echo "Removed. Open a new shell to re-clone them, or run: source \$ZDOTDIR/plugins.zsh"
}

local entry
for entry in "${ZPLUGIN_LIST[@]}"; do
  _zplugin_load ${=entry}
done
