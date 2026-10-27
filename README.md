# HUM · the grid, heard

The power grid's frequency, heard live from a room's wiring through a guitar pickup, and a Torus Station answering in two bands, decided by a program whose compiler proves what it can never do.

Hard Tech Week 2026, Salt Lake City. Entered for the Torus bounty ("software that knows when the grid is jammed and stays out of traffic") and the Nucleus / Startup State open call.

![HUM during the replay of a real grid event: the frequency falls, Spin fires, the reason reads in words](pitch/hero.png)

## In one breath

Every wire in a building hums at the grid's frequency, and that frequency is set by every generator on the Western Interconnection together: it sags when the whole grid is short, and the rate it falls says how fast a plant just dropped. A guitar pickup hears the hum. The ear in this directory reads it to the millihertz three independent ways. A Torus Station, modeled from Torus's published figures, answers in two bands: Spin takes the milliseconds, Pulse takes the hours, and when the hum dies the Station carries the building. The program that decides is written in Mentl, and its compiler proves it cannot reach the network, cannot touch the filesystem, cannot allocate mid-decision and cannot command either machine past its rating, through every call. Every decision says why, in words.

## What is real and what is simulated

- **Real:** the hum and its frequency (live or from a recording made in the room), PacifiCorp East's hours from EIA-930, the 9 August 2019 disturbance on the GB grid from NESO's open one-second data (transposed to 60 Hz per unit and labeled so on every screen), the proofs.
- **Simulated, and labeled where it appears:** the Station's response (Spin 100 kW / 10 kWh, Pulse 300 kW / 1,200 kWh, from Torus's published 10C, six-minute and four-hour figures), the building's load, the mesh screen.

## Run it

```
cargo build -p sonido-analysis --release --example grid_ear      # the ear
python3 -I build_data.py --out data                              # PacifiCorp East's hours and the event (EIA_API_KEY optional)
./run.sh live        # the guitar on the interface, through PipeWire
./run.sh wav samples/hum_home.wav
./run.sh replay      # the real event
STUB=1 ./run.sh sample samples/ear_event.ndjson   # no Mentl needed: the stand-in controller
```

The page is at http://127.0.0.1:8787/. Keys: `E` replay event · `I` island · `P` certificate · `A` the compiler's words · `R` refusal · `T` table · `M` mesh · `S` sound · `B` bright room · `0` reset. The sixty-second venue drill is `setup.md`.

The Mentl programs live in the Mentl repository under `examples/grid/`: `station.mn` (the controller), `station-leak.mn` (the refusal twin), `listen.mn` (the learner), `predict.mn`, `score.mn`. `mentl check examples/grid/station-leak.mn` is the refusal; `mentl audit examples/grid/station.mn` is the certificate.

## The pieces

| Piece | Where | What it does |
| --- | --- | --- |
| The estimator | `crates/sonido-core/src/grid.rs` | `no_std`: three bandpasses on the hum's harmonics, the loudest tracked, periods between zero crossings read to a fraction of a sample; frequency over 100 ms and 1 s, rate of change over 300 ms, level, and "the hum is gone". Shared with the pedal. |
| The ear | `crates/sonido-analysis/examples/grid_ear.rs` | Live float stream, WAV, tone, replay or silence in; a spectral estimate and THD from a two-second window; one C1 line every 50 ms. |
| The director | `director.py` | Spawns the ear and the controller, enriches the lines with the hour, the rush window and the clean share, keeps the traces and the ledger, serves the page, records the session. |
| The page | `index.html` | The five panels, the overlays, the sound, the playback mode. One file, no dependencies. |
| The data | `build_data.py`, `data/` | PacifiCorp East's demand, day-ahead forecast and clean share by hour; the event. |
| The contracts | `CONTRACTS.md` | The line formats every process speaks. |
| The brief | `MENTL_BRIEF.md` | What the Mentl session built from. |

## Measured

On a synthesized hum with harmonics and noise at −30 dB: the one-second reading within 0.5 mHz, the spectral reading within 0.2 mHz, the rate of change under 0.023 Hz/s at rest. A replayed trip falling at 0.20 Hz/s crosses the 0.10 Hz/s trigger 250 ms after it starts. A hum cut to silence reads lost 350 ms later.

## Before kickoff and this week

`./ledger.sh ~/mentl` prints every commit in both repositories since Monday Oct 26 at 4:00 PM MDT, with timestamps, and the age of each repository. What existed before: Mentl (a self-hosting compiler with effect proofs, years of commits), sonido (36 effects, the plugin, the browser editor, the pedal), the Wasatch piece. What was built this week: everything in this directory, the grid module, and the programs under `examples/grid/`.
