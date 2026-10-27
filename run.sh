#!/usr/bin/env bash
# HUM: one command per mode. Starts the director (which starts the ear and
# the controller), then opens the page in a kiosk window.
#
#   ./run.sh live                 the guitar on the Scarlett, through PipeWire
#   ./run.sh wav <path.wav>       a recording, in real time
#   ./run.sh pedal [/dev/ttyACM0] the pedal's serial line
#   ./run.sh replay               the real event, then back to nothing
#   ./run.sh sample [file]        a sample file (development)
#
# Environment:
#   MENTL_DIR   the Mentl checkout holding examples/grid/station.mn (default ~/mentl)
#   MENTL_BIN   the mentl command (default: mentl on PATH)
#   STUB=1      use the in-process stand-in controller instead of Mentl
#   NO_BROWSER=1  do not open the page
#   CAPTURE     the capture command for live mode
#               (default: arecord -D pipewire -t raw -f FLOAT_LE -r 48000 -c 1 -)
set -euo pipefail
cd "$(dirname "$0")"
mode="${1:-live}"; shift || true
EAR="../../target/release/examples/grid_ear"
if [ ! -x "$EAR" ]; then
  echo "building the ear..." >&2
  (cd ../.. && cargo build -p sonido-analysis --release --example grid_ear)
fi
args=(--mode "$mode" --ear "$EAR")
case "$mode" in
  live)    ;;
  wav)     args+=(--wav "${1:?a WAV path}") ;;
  pedal)   args+=(--serial "${1:-/dev/ttyACM0}") ;;
  replay)  ;;
  sample)  args+=(--sample "${1:-samples/ear_tone.ndjson}") ;;
  *) echo "unknown mode $mode" >&2; exit 2 ;;
esac
[ -n "${CAPTURE:-}" ] && args+=(--capture "$CAPTURE")
if [ "${STUB:-0}" = "1" ]; then args+=(--stub-controller); else
  args+=(--mentl-dir "${MENTL_DIR:-$HOME/mentl}" --mentl-bin "${MENTL_BIN:-mentl}")
fi
if [ "${NO_BROWSER:-0}" != "1" ]; then
  ( sleep 2
    for b in chromium chromium-browser google-chrome firefox; do
      if command -v "$b" >/dev/null 2>&1; then
        case "$b" in
          firefox) "$b" --kiosk "http://127.0.0.1:8787/index.html" >/dev/null 2>&1 & ;;
          *) "$b" --kiosk --app="http://127.0.0.1:8787/index.html" --autoplay-policy=no-user-gesture-required >/dev/null 2>&1 & ;;
        esac
        break
      fi
    done ) &
fi
exec python3 -I director.py "${args[@]}"
