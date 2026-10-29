#!/usr/bin/env bash
# Puts the one file to upload in a folder at the top of the repository,
# "Mentl - Morgan Espitia": HUM-Morgan-Espitia.pdf, the hosted tour as pages
# in its own order, with the demo and GitHub links on its slides. The folder
# is emptied first, so it holds exactly what to upload. Run
# `node pitch/export.js` first, so the PDF matches the page and the slides.
#   ./pitch/submission.sh
set -euo pipefail
cd "$(dirname "$0")/.."
out="Mentl - Morgan Espitia"
rm -rf "$out"
mkdir -p "$out"
cp pitch/HUM-Morgan-Espitia.pdf "$out/HUM-Morgan-Espitia.pdf"
ls -l "$out"
echo "Upload this one file. The demo it links to: https://ampactor.dev/hum"
