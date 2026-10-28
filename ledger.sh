#!/usr/bin/env bash
# The before-and-this-week ledger: every commit in HUM, sonido and Mentl
# since the hackathon kicked off (Monday Oct 26, 4:00 PM MDT), with
# timestamps, for slide three and the README. Pass the Mentl checkout as $1
# (default: MENTL_DIR, then the checkout the mentl command runs from). SONIDO
# names sonido's checkout (default: ~/sonido or ~/Projects/sonido). A
# repository that isn't there is named on stderr, never skipped silently.
set -euo pipefail
export TZ=America/Denver
export PATH="$HOME/.local/bin:$PATH"
since="2026-10-26T16:00:00-06:00"
mentl_home() { sed -n 's/^MENTL_HOME="\(.*\)"$/\1/p' "$(command -v mentl)" 2>/dev/null | head -1 || true; }
mentl="${1:-${MENTL_DIR:-$(mentl_home)}}"
mentl="${mentl:-$HOME/mentl}"
sonido="${SONIDO:-}"
if [ -z "$sonido" ]; then
  for d in "$HOME/sonido" "$HOME/Projects/sonido"; do
    if [ -d "$d/.git" ]; then sonido="$d"; break; fi
  done
fi
repos=()
for repo in "$(cd "$(dirname "$0")" && pwd)" "${sonido:-$HOME/sonido}" "$mentl"; do
  if [ -d "$repo/.git" ]; then repos+=("$repo"); else echo "ledger: no repository at $repo, so it is left out" >&2; fi
done
echo "## This week (since Monday Oct 26, 4:00 PM MDT)"
echo
for repo in "${repos[@]}"; do
  name=$(basename "$repo")
  n=$(git -C "$repo" log --since="$since" --oneline HEAD | wc -l | tr -d ' ')
  echo "### $name: $n commits"
  echo
  git -C "$repo" log --since="$since" HEAD --date=format:'%a %H:%M' --pretty='- %ad  %s' | head -60
  echo
done
echo "## Before kickoff"
echo
for repo in "${repos[@]}"; do
  name=$(basename "$repo")
  first=$(git -C "$repo" log --date=short --pretty='%ad' HEAD | tail -1)
  before=$(git -C "$repo" rev-list --count --before="$since" HEAD)
  if [ "$before" -eq 0 ]; then
    echo "- $name: nothing before kickoff; born this week"
  else
    echo "- $name: $before commits before kickoff, the first on $first"
  fi
done
