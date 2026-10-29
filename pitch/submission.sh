#!/usr/bin/env bash
# Gathers everything to upload into one folder at the top of the repository,
# "Mentl - Morgan Espitia": the four PDFs, the stage picture, the budget and
# a README. It copies over the files it makes and never deletes anything, so
# a file added to the folder by hand stays. Run `node pitch/export.js` first,
# so the PDFs match the slides.
#   ./pitch/submission.sh
set -euo pipefail
cd "$(dirname "$0")/.."
out="Mentl - Morgan Espitia"
mkdir -p "$out"
cp pitch/show.pdf              "$out/1-HUM-pitch-deck.pdf"
cp pitch/torus.pdf             "$out/2-HUM-Torus-leave-behind.pdf"
cp pitch/nucleus.pdf           "$out/3-Mentl-Nucleus-deck.pdf"
cp pitch/nucleus-one-pager.pdf "$out/4-Mentl-Nucleus-one-page-plan.pdf"
cp pitch/hero.png              "$out/5-HUM-stage-during-the-2019-replay.png"
cp pitch/budget.md             "$out/6-Mentl-budget-for-the-10000.md"
cp pitch/submission-readme.txt "$out/README.txt"
ls -l "$out"
