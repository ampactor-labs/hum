# The Mentl half of HUM

Three programs in the Mentl repository, under `examples/grid/`, do HUM's deciding and learning. They read the line formats in `CONTRACTS.md`. Each file's opening comment says what it does and how to run it. This page says how the three fit HUM and what was measured.

## station.mn: the controller

It reads one line per reading from the director and answers each with one decision line. The function that decides, `decide`, declares five restrictions in its signature: no memory allocation, no network, no file system, no call outside the program at all, and no way to stop the program with an error (`!Alloc + !Network + !Filesystem + !WASI + !Trap`). The compiler proves all five through every function `decide` calls.

The decision commands each machine through an operation of the effect `Station`, and the machine answers with the power it gives, typed to its rating: ±100 kW for the flywheel, ±300 kW for the battery. The compiler proves every answer stays inside that range. The frequency the fast rules act on must lie between 55 and 65 Hz. Every number is an integer in thousandths, read from the line's text, so the decision never rounds a floating-point number.

The rules:

- Within 36 mHz of 60 Hz, nothing happens.
- Beyond that, the flywheel pushes in proportion, reaching full power 200 mHz past the band.
- If the frequency falls or rises faster than 100 mHz per second, the flywheel goes to full power for 2 to 10 seconds. The page calls this an event and holds the word while the flywheel pushes at least 10 kW, plus two seconds.
- In the rush-hour window, the battery runs the building at 300 kW. In a clean hour, it charges at 150 kW, up to 95 percent, but never while the flywheel is pushing because the grid is low: charging then would add load to a falling grid.
- When a hum that was heard disappears, or drops 30 dB below its ten-second average, for six readings in a row, the Station keeps the building on: the flywheel for the first two seconds, the battery after that. Two good readings end it.

The Station is a model built from Torus's published figures: the flywheel 100 kW and 10 kWh, the battery 300 kW and 1,200 kWh.

Measured on the pinned compiler:

- `samples/ear_event.ndjson`: the event starts on the reading where the fall crosses 100 mHz per second, "falling at 129 mHz per second, past 100".
- `samples/ear_tone.ndjson`: no event, and the flywheel tops up from the battery at 20 kW.
- In the bundled recording, the median decision takes 0.6 ms, counting the line's trip from the director to the controller and back. 97 in 100 take under 1 ms, and the slowest took 33 ms. The times move with the machine's load: an earlier recording had a median of 0.1 ms. The first line also waits for the controller to start.

What is not proven. Every claim in the controller is proven, the power limits included: `mentl check examples/grid/station.mn` prints nothing, and it would print any claim it could not prove. The decision is proven never to stop the program with an error. Every function the controller defines is proven never to stop with an error, the cut that copies the reading's timestamp included: the program states the cut's bounds where it cuts, and the compiler proves them. One byte-range check inside the library's print routine, which cannot fail, is not proven yet; Mentl's PLAN names that step. Memory no longer grows: each reading runs inside an arena, and the peak is the same after 300,000 readings as after 60,000. The pedal does not run the controller yet because its chip has no WebAssembly engine. One limit is in Mentl itself: `!Network` on `decide` covers every function `decide` calls, and any function passed to it, but not the handler that answers `decide`'s own operations, `station`, which `main` installs around it. HUM's claim does not rest on that gap: `station` answers `spin`, `pulse` and `because` with arithmetic, its one printing arm, `report`, runs after `decide` returns, and the first line of `mentl audit` says that nothing in the whole program uses the network. The compiled controller imports three host functions, `fd_read`, `fd_write` and `proc_exit`, and no socket. Mentl's PLAN names the rule that closes the gap, under the soundness core.

## station-leak.mn: the copy the compiler refuses

The same controller with one line a reasonable engineer might add: read the hour's electricity price online, inside the fast decision, so that in rush hour the battery runs at full power only when the price is above $50 a megawatt-hour. `mentl check examples/grid/station-leak.mn` refuses it with `E_EffectMismatch` and names the path the network takes: `decide` calls `price_m`, which calls `fetch_param`, which is a network operation. The full text is `pitch/refusal.txt`.

## listen.mn: the learner

One number learns the hum's frequency from a 480 Hz copy of the signal. A pure tone obeys x[n] = a·x[n−1] − x[n−2] with a = 2·cos ω, so the program predicts each sample from the two before it and nudges `a` against the slope of the squared error. The compiler derives that slope itself, from `d(e * e)` under `~> grad(a)`. A low-pass filter at 80 Hz keeps the hum's harmonics out, and both stages are declared `!Alloc`. Once a second it prints a line such as `{"hz_learned":60.000312}`.

Measured: within 5 mHz of the zero-crossing reading on a hum that wobbles ±20 mHz, and 60.05000 on a 60.050 Hz tone. It trails a fast fall, so the stage does not show it.

## The compiler's output, captured under `pitch/`

- `refusal.txt`: `mentl check examples/grid/station-leak.mn`.
- `audit.txt`: `mentl audit examples/grid/station.mn`.
- `why.txt`: `mentl why examples/grid/station.mn decide`, then the same question about `Network`, `Alloc`, `Filesystem`, `WASI` and `Trap`. Each answer says `decide` never uses it.
- `gate.txt`: a `mentl mcp` session. A clean decision is proposed and proven, then the same decision with a price lookup is refused and nothing is built.
