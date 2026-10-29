# HUM

HUM measures the power grid's frequency through a guitar pickup and shows a model of a Torus Station deciding what to do about it. The software that decides is written in Mentl, a language I built: its rules are written into the code, the compiler checks them through every function the decision calls, and a version that breaks one does not build. So the decision never reaches the internet, never allocates memory and never stops with an error.

Hard Tech Week 2026, Salt Lake City. Entered for the Torus bounty ("software that knows when the grid is jammed and stays out of traffic") and the Nucleus × Startup State open call. Every commit here is from the hackathon week. What existed before lives in [sonido](https://github.com/ampactor-labs/sonido) and [Mentl](https://github.com/ampactor-labs/mentl).

![The stage during the replayed 2019 grid failure: the frequency falls and the flywheel pushes 100 kW](pitch/hero.png)

## What it does

Every wire in a building hums at the power grid's frequency. The whole Western grid, from Alberta to Baja, shares that one number. It sags when the grid is short of power, and how fast it falls says how big the shortfall is.

A guitar pickup picks up the hum. The ear, a program built on my audio library sonido, reads the frequency to a thousandth of a hertz and runs sonido's tuner on it.

A model of a Torus Station decides what to do. Its flywheel handles fast changes and its battery carries load for hours. In rush hour, which EIA's hourly data marks, the battery runs the building. When the frequency falls fast, the flywheel pushes. When the hum disappears, the Station keeps the building on.

The decision is written in Mentl. Its rules are in the code, and the compiler checks them through every function the decision calls: it never reaches the network, a file or the clock, never allocates memory and never stops with an error. A copy of the program with one price lookup added inside the decision does not build, and the refusal names the line. What is not proven is that the decisions are good; recordings test them.

## What is real and what is simulated

- **Real:** the hum and its frequency when the ear listens live or to a recording made in a room; PacifiCorp East's hourly demand from EIA-930; the 9 August 2019 failure on Britain's grid, from National Grid ESO's one-second data, transposed to 60 Hz and labeled on screen; the compiler's proofs.
- **Simulated, and labeled on screen:** the Station, modeled from Torus's published figures (100 kW from the flywheel for six minutes, 300 kW from the battery for four hours); the building's load; and the test hum, a synthesized 60 Hz hum with a small wobble, which the bundled session plays on unless it was recorded live.

## Run it

```
(cd ear && cargo build --release)                 # the ear, built against sonido from GitHub
python3 -I build_data.py --out data               # PacifiCorp East's hours and the 2019 event (EIA_API_KEY optional)
./run.sh live                                     # the guitar on the audio interface, through PipeWire
./run.sh pedal                                    # the guitar into the pedal, the pedal on USB
./run.sh wav samples/event_gb.wav                 # a recording: here, the 2019 event as sound
./run.sh replay                                   # the 2019 event, from eight seconds before the fall
STUB=1 ./run.sh sample samples/ear_event.ndjson   # without Mentl: a stand-in controller written in Python
python3 -I record.py --mode live                  # re-record the bundled session on the room's own hum
```

The page is at http://127.0.0.1:8787/. It opens on the stage: the frequency, sonido's tuner, the Station's two machines, and one sentence about what is happening.

Keys: the page opens on the pitch, one show for both rooms. Space, a clicker's Page Down or the pedal's footswitch 1 runs the next beat, and the left arrow or footswitch 2 steps back one · `0` the title · `H` tomorrow's noon · `Shift+E` replay the 2019 event · `Shift+I` cut the hum · `P` proven · `R` refused · `K` thank you · `A` the compiler's own text on a card · `D` the engineers' dashboard · `Esc` close · `Shift+Q` quit: the director stops and the window closes. The dashboard adds `G` the gate, `T` the raw lines, `M` the mesh, `S` sound and `B` a bright-room palette; `Shift+P` and `Shift+R` open the detailed proof and refusal. The venue drill is `setup.md`, and the pitch itself is `pitch/script.md`.

Served as plain files with no director, as at https://ampactor.dev/hum, the page is a tour of the same fifteen steps the presenter gives, at the viewer's pace: the arrows on screen or on the keyboard, or a swipe on a phone. Nothing moves on to the next step by itself. A live screen's step plays its stretch of `sessions/default.ndjson` once and holds, and ↻ plays it again; the session is about four minutes recorded with the real controller by `python3 -I record.py`. On a phone held upright the stage stacks into one column. `samples/event_gb.wav` is the 2019 event rendered as sound: 95 seconds at 8 kHz.

The Mentl programs live in the Mentl repository under `examples/grid/`. `station.mn` decides, `station-leak.mn` is the copy with a price lookup that the compiler refuses, and `listen.mn` learns the frequency. `mentl check examples/grid/station-leak.mn` shows the refusal, and `mentl why examples/grid/station.mn decide WASI` shows that the decision makes no call outside the program. `MENTL_BRIEF.md` has the details.

## The pieces

| Piece | Where | What it does |
| --- | --- | --- |
| The estimator | sonido, `crates/sonido-core/src/grid.rs` | Filters the hum's first three harmonics, follows the loudest, and times its zero crossings to a fraction of a sample. It reports the frequency over 100 ms and over 1 s, how fast it is changing, the level, and when the hum is gone. The ear and the pedal share it. |
| The ear | `ear/` | A program built on sonido. It takes live audio, a WAV file, a test tone, the 2019 replay or silence, and prints one line every 50 ms: the estimator's readings, a spectral check, the distortion, sonido's tuner reading and a scope trace for the page. |
| The pedal | sonido, `crates/sonido-daisy/examples/grid_pedal.rs` | The same estimator on a Daisy Seed in a Hothouse pedal. It sends its lines over USB, blinks an LED faster the further the frequency is from 60 Hz, and its footswitches and first toggle type the page's keys. |
| The director | `director.py` | Starts the ear and the controller, adds the hour, the rush window and the clean share to each line, serves the page, and records each session. |
| The page | `index.html` | The stage, the three cards and the engineers' dashboard. It plays a recorded session when no director answers. One file with no dependencies. |
| The data | `build_data.py`, `data/` | PacifiCorp East's demand, day-ahead forecast and clean share by hour; the event. |
| The pitch | `pitch/` | The show's slides, the Nucleus deck, the Torus leave-behind, the one-page plan, the script with its answers to likely questions, `shots.js`, which takes the slides' pictures from the bundled session, `export.js`, which writes the PDFs, among them `HUM-Morgan-Espitia.pdf`, the whole tour as one file, and `submission.sh`, which puts that one file in the folder `Mentl - Morgan Espitia` to upload. |
| The contracts | `CONTRACTS.md` | The line formats the ear, the director, the controller and the page use. |

## Measured

On a synthesized hum with harmonics and noise at −30 dB, the one-second reading is within 0.5 mHz and the spectral reading within 0.2 mHz, and the rate of change at rest stays under 0.023 Hz/s. A replayed trip falling at 0.20 Hz/s crosses the 0.10 Hz/s trigger 250 ms after it starts. A hum cut to silence reads as lost 350 ms later. sonido's tuner reads a 60.000 Hz tone as B1 at +0.2 cents and a 59.300 Hz tone at −20.2 cents.

## Before kickoff and this week

`./ledger.sh` prints every commit made in this repository, in sonido and in Mentl since Monday 26 October at 4:00 PM MDT, each with its time, and how long each repository has existed.
