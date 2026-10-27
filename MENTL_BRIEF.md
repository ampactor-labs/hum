# The Mentl half of HUM

Three user programs in the Mentl repository, `github.com/ampactor-labs/mentl`, under `examples/grid/`, written against `CONTRACTS.md` and the samples here. They are the hard-tech center of the Nucleus pitch and the closing beat of the Torus pitch: nobody in the energy industry ships a controller whose compiler proves it cannot reach the network while deciding. Each program's head comment says what it is and how to run it; this page says how the three fit HUM and what was measured when they landed.

## station.mn, the controller

Reads enriched ear lines (C1e) on stdin and answers each with a decision line (C2) on the same tick. `decide` is declared `!Alloc + !Network + !Filesystem + !WASI` and the compiler proves the three through every call. Every command passes a refinement type (`SpinW` ±100 kW, `PulseW` ±300 kW, `Soc` 0 to 1000) and the reading the bands act on is a `GridMhz` (55 to 65 Hz). Every number is an integer in milli-units read off the line's text, so the decision never rounds a float and never reaches the one conversion that can trap. The Station is modeled from Torus's published figures (Spin 100 kW / 10 kWh, Pulse 300 kW / 1,200 kWh) and labeled so.

The rules, as the program states them: a 36 mHz deadband; a droop that reaches full Spin at 200 mHz past the band; the reflex at 100 mHz/s, full Spin, held 2 to 10 s; EVENT for as long as the fast band pushes at least 10 kW and two seconds after; RUSH discharging Pulse at 300 kW through the window; a clean hour charging Pulse at 150 kW to 95 percent; ISLAND two lines after the hum, once heard, is 30 dB under its ten-second mean or gone, Spin for two seconds and Pulse after; two lines of the hum back end it.

Measured on the pinned boot, the samples enriched by hand:

- `ear_event.ndjson`: EVENT on the line where the rate of change crosses 100 mHz/s, "falling at 129 mHz per second, past 100"; the reflex holds ten seconds; the droop carries Spin at 52 kW at −140 mHz and the mode stays EVENT until the deviation is inside 56 mHz, 31 s later; then RUSH.
- `ear_island.ndjson`: the reflex at the fall, then ISLAND two lines after the hum dies, "the hum died, 105.8 dB under its mean: Spin carries the first seconds", Pulse carrying 200 kW after.
- `ear_tone.ndjson`: GRID throughout, "within 36 mHz of 60; Spin topping up from Pulse at 20 kW".

## station-leak.mn, the twin that refuses

The controller line for line with one addition a reasonable engineer would write: the hour's price read live inside the reflex, so Pulse leans harder into an expensive hour. `mentl check examples/grid/station-leak.mn` refuses: `E_EffectMismatch`, declared as decide; Network enters through `price_m` → through `fetch_param` → declared as fetch_param, an op of Network declared at dsp/signal:66:1. The chain is the point, hop by hop from the oath to the op. The text is `pitch/refusal.txt`.

## listen.mn, the learner

One coefficient learns the hum's frequency from the 480 Hz stream (`hum_480.txt`): a sinusoid obeys x[n] = a·x[n−1] − x[n−2] with a = 2 cos ω, the squared prediction error is the chain the reading differentiates, `d(e * e)` under `~> grad(a)`, and the coefficient moves against the slope each sample, lesson 09's step. A four-pole low-pass at 80 Hz, its lines owned by the stage, keeps the hum's harmonics from bending the predictor; the step is normalized by a smoothed energy. Both stages are `!Alloc`. It prints `{"hz_learned":60.000312}` once a second (C7). Measured: within 5 mHz of the stream's own zero crossings on the recorded hum, which wobbles ±20 mHz; 60.05000 on a 60.050 Hz sine.

## The captures, under `pitch/`

- `refusal.txt`: `mentl check examples/grid/station-leak.mn`.
- `audit.txt`: `mentl audit examples/grid/station.mn`, the certificate: `decide` Real-time safe (proven zero allocation), the module Sandbox (proven no network access).
- `why.txt`: `mentl why examples/grid/station.mn decide`, and with `Network`, `Alloc`, `Filesystem`, `WASI`: "the row of decide carries no Network", "the row of decide carries no WASI": no host call of any kind inside a decision.
- `gate.txt`: `mentl mcp`, the proof gate on stdio: a clean reflex proposed, PROVEN; the same reflex with a price read inside, REFUSED, nothing emitted.

## What was cut

`predict.mn`, `score.mn` and the resume recording were planned and cut: the EIA window suffices, the piece did not serve the pitch, and durable computation is the compiler's own `resume` verb. The brief that specified them was superseded by the programs themselves.
