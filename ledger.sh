#!/usr/bin/env bash
# The before-and-this-week ledger: every commit in both repositories since
# the hackathon kicked off (Monday Oct 26, 4:00 PM MDT), with timestamps,
# for slide three and the README. Pass the Mentl checkout as $1 (default ~/mentl).
set -euo pipefail
export TZ=America/Denver
since="2026-10-26T16:00:00-06:00"
mentl="${1:-$HOME/mentl}"
echo "## This week (since Monday Oct 26, 4:00 PM MDT)"
echo
for repo in "$(cd "$(dirname "$0")" && pwd)" "${SONIDO:-$HOME/sonido}" "$mentl"; do
  [ -d "$repo/.git" ] || continue
  name=$(basename "$repo")
  n=$(git -C "$repo" log --since="$since" --oneline HEAD | wc -l | tr -d ' ')
  echo "### $name: $n commits"
  echo
  git -C "$repo" log --since="$since" HEAD --date=format:'%a %H:%M' --pretty='- %ad  %s' | head -60
  echo
done
echo "## Before kickoff"
echo
for repo in "$(cd "$(dirname "$0")" && pwd)" "${SONIDO:-$HOME/sonido}" "$mentl"; do
  [ -d "$repo/.git" ] || continue
  name=$(basename "$repo")
  first=$(git -C "$repo" log --date=short --pretty='%ad' HEAD | tail -1)
  before=$(git -C "$repo" rev-list --count --before="$since" HEAD)
  if [ "$before" -eq 0 ]; then
    echo "- $name: nothing before kickoff; born this week"
  else
    echo "- $name: $before commits before kickoff, the first on $first"
  fi
done
