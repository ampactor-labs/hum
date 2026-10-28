#!/usr/bin/env bash
# The before-and-this-week ledger: every commit in HUM, sonido and Mentl
# since the hackathon kicked off (Monday Oct 26, 4:00 PM MDT), with
# timestamps, for slide three and the README. Pass the Mentl checkout as $1
# (default: MENTL_DIR, then the checkout the mentl command runs from). SONIDO
# names sonido's checkout (default: ~/sonido or ~/Projects/sonido). sonido is
# read at the branch the ear builds against (ear/Cargo.toml), so fetch it
# first; the others at their checked-out commit. A repository that isn't
# there is named on stderr, never skipped silently.
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
here="$(cd "$(dirname "$0")" && pwd)"
sonido_branch=$(sed -n 's/^sonido-core = .*branch = "\([^"]*\)".*/\1/p' "$here/ear/Cargo.toml" | head -1)
repos=() refs=()
for repo in "$here" "${sonido:-$HOME/sonido}" "$mentl"; do
  if [ ! -d "$repo/.git" ]; then echo "ledger: no repository at $repo, so it is left out" >&2; continue; fi
  ref=HEAD
  if [ "$repo" = "${sonido:-}" ] && [ -n "$sonido_branch" ]; then
    if git -C "$repo" rev-parse -q --verify "origin/$sonido_branch" >/dev/null; then ref="origin/$sonido_branch"
    else echo "ledger: sonido has no origin/$sonido_branch, the branch the ear builds against, so its checked-out commit is read" >&2; fi
  fi
  repos+=("$repo") refs+=("$ref")
done
echo "## This week (since Monday Oct 26, 4:00 PM MDT)"
echo
for i in "${!repos[@]}"; do
  repo="${repos[$i]}" ref="${refs[$i]}"
  name=$(basename "$repo")
  n=$(git -C "$repo" log --since="$since" --oneline "$ref" | wc -l | tr -d ' ')
  echo "### $name: $n commits"
  echo
  git -C "$repo" log --since="$since" "$ref" --date=format:'%a %H:%M' --pretty='- %ad  %s' | head -60
  echo
done
echo "## Before kickoff"
echo
for i in "${!repos[@]}"; do
  repo="${repos[$i]}" ref="${refs[$i]}"
  name=$(basename "$repo")
  first=$(git -C "$repo" log --date=short --pretty='%ad' "$ref" | tail -1)
  before=$(git -C "$repo" rev-list --count --before="$since" "$ref")
  if [ "$before" -eq 0 ]; then
    echo "- $name: nothing before kickoff; born this week"
  else
    echo "- $name: $before commits before kickoff, the first on $first"
  fi
done
