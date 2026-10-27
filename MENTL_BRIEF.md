# The Mentl half of HUM

Three programs in the Mentl repository, under `examples/grid/`, do HUM's deciding and learning. They read the line formats in `CONTRACTS.md`. Each file's opening comment says what it does and how to run it. This page says how the three fit HUM and what was measured.

## station.mn: the controller

It reads one line per reading from the director and answers each with one decision line. The function that decides, `decide`, makes four promises in its signature: no memory allocation, no network, no file system, and no host call of any kind (`!Alloc + !Network + !Filesystem + !WASI`). The compiler proves all four through every function `decide` calls.

Power commands are clamped in code, the flywheel to ±100 kW and the battery to ±300 kW, and their types state those ranges. The frequency the fast rules act on must lie between 55 and 65 Hz. Every number is an integer in thousandths, read from the line's text, so the decision never rounds a floating-point number.

The rules:

- Within 36 mHz of 60 Hz, nothing happens.
- Beyond that, the flywheel pushes in proportion, reaching full power 200 mHz past the band.
- If the frequency falls or rises faster than 100 mHz per second, the flywheel goes to full power for 2 to 10 seconds. The page calls this an event and holds the word while the flywheel pushes at least 10 kW, plus two seconds.
- In the rush-hour window, the battery runs the building at 300 kW. In a clean hour, it charges at 150 kW, up to 95 percent.
- When a hum that was heard disappears, or drops 30 dB below its ten-second average, for six readings in a row, the Station keeps the building on: the flywheel for the first two seconds, the battery after that. Two good readings end it.

The Station is a model built from Torus's published figures: the flywheel 100 kW and 10 kWh, the battery 300 kW and 1,200 kWh.

Measured on the pinned compiler:

- `samples/ear_event.ndjson`: the event starts on the reading where the fall crosses 100 mHz per second, "falling at 129 mHz per second, past 100".
- `samples/ear_tone.ndjson`: no event, and the flywheel tops up from the battery at 20 kW.
- In the director, each decision takes under a millisecond on the laptop.

What is not proven. The audit lists twelve claims it could not settle, in seven functions, two of them inside `decide`. The program can trap. The loop that reads and writes text around the decision keeps about 8 KB per reading: harmless on the laptop for hours, but on the pedal's 64 MB it would last about seven minutes. That, together with the pedal having no WebAssembly engine, is why the pedal does not run the controller yet.

## station-leak.mn: the copy the compiler refuses

The same controller with one line a reasonable engineer might add: read the hour's electricity price online, inside the fast decision, so the battery leans harder into an expensive hour. `mentl check examples/grid/station-leak.mn` refuses it with `E_EffectMismatch` and names the path the network takes: `decide` calls `price_m`, which calls `fetch_param`, which is a network operation. The full text is `pitch/refusal.txt`.

## listen.mn: the learner

One number learns the hum's frequency from a 480 Hz copy of the signal. A pure tone obeys x[n] = a·x[n−1] − x[n−2] with a = 2·cos ω, so the program predicts each sample from the two before it and nudges `a` against the slope of the squared error. The compiler derives that slope itself, from `d(e * e)` under `~> grad(a)`. A low-pass filter at 80 Hz keeps the hum's harmonics out, and both stages promise `!Alloc`. Once a second it prints a line such as `{"hz_learned":60.000312}`.

Measured: within 5 mHz of the zero-crossing reading on a hum that wobbles ±20 mHz, and 60.05000 on a 60.050 Hz tone. It trails a fast fall, so the stage does not show it.

## The compiler's output, captured under `pitch/`

- `refusal.txt`: `mentl check examples/grid/station-leak.mn`.
- `audit.txt`: `mentl audit examples/grid/station.mn`.
- `why.txt`: `mentl why examples/grid/station.mn decide`, then the same question about `Network`, `Alloc`, `Filesystem` and `WASI`. Each answer says `decide` carries none of them.
- `gate.txt`: a `mentl mcp` session. A clean decision is proposed and proven, then the same decision with a price lookup is refused and nothing is built.
