# Brief for the Mentl session: HUM's programs

You are writing the Mentl half of HUM, the Hard Tech Week entry judged Wednesday Oct 28 at 5:00 PM MDT. The whole build: the grid's frequency heard live from a room's wiring through a guitar pickup (a Rust ear in the sonido repository), a Torus Station modeled from Torus's published figures that answers in two bands, and the program that decides, written in Mentl with its negative capabilities proven and every decision explained. Your programs are the hard-tech center of the Nucleus pitch and the closing beat of the Torus pitch. Nobody in the energy industry ships a controller whose compiler proves it cannot reach the network while deciding. That is what these programs show.

Everything you need from the other side is in the HUM repository, `github.com/ampactor-labs/hum`, on main: `CONTRACTS.md` (the line formats) and `samples/` (real input lines: a tone, the synthetic event, the real GB event, the island). Until the samples land, write three C1e lines by hand from the contract and develop against those.

## Rules for this work

- These are user programs under `examples/grid/`. They are judged by `mentl check`, `mentl fmt --check` and `mentl run`. No compiler change unless a program hits a refusal the language should not give, and then the fix is a landing of its own under your usual discipline.
- No test fixtures, no README: each program's head comment says what it is and how to run it, in the manner of `examples/wasatch/inversion.mn`. The obey gate refuses a new `.md` file, so do not add one.
- Push to the Mentl repository's main as each program lands; the other session pulls main to integrate and never commits to your tree. Report back, through the user, the exact commands you ran and their output, especially anything that did not behave as this brief assumes.
- Priority order: the two probes now, then `station.mn` and `station-leak.mn`, then `listen.mn`, then `predict.mn`, `score.mn`, the resume recording and the agent transcript.

## The contracts you touch

Input, one line per 50 ms on stdin, C1e (the director adds the last four fields; the samples lack them, so add them yourself when you test against the samples):

```
{"t":1761620000.50,"hz_fast":59.9810,"hz":59.9830,"hz_stft":59.9830,"rocof":-0.004,"thd":3.1,"level_db":-18.5,"harmonic":1,"source":"live","hour_local":21.4,"rush":0,"clean":0.31,"offset_mhz":2.1}
```

Before the ear locks, `hz_fast`, `hz`, `hz_stft` and `rocof` are `null`. Treat a null reading as "no decision yet": mode GRID, zero power, reason "listening".

Output, one line per input line on stdout, C2, integers in milli-units (the library has `print_int` and `++`; there is no float printer, so never print a float), strings for words:

```
{"t_ms":1761620000500,"mode":"EVENT","spin_w":100000,"pulse_w":0,"spin_soc_m":940,"pulse_soc_m":620,"reason":"falling at 310 mHz per second, past 100"}
```

`mode` is one of `GRID`, `EVENT`, `RUSH`, `ISLAND`. Power is watts, positive discharging into the facility, negative charging. State of charge is thousandths. The reason is one sentence in words that a non-engineer reads, naming the rule and the number that fired it, with milli-units ("falling at 310 mHz per second, past 100"; "rush hour, hour 18 of 17 to 21"; "the hum died, 42 dB under its mean").

## Probe one, the stream (first thing you run)

A fifteen-line program: loop on `read_stdin_line` (lib/io.mn), stop on an empty line, `parse_float` (lib/strings.mn) one field out of the line, print a C2-shaped line with `print_int` and `++`. Run it as

```
(for i in 1 2 3; do echo '{"hz_fast":59.98}'; sleep 1; done) | mentl run probe.mn
```

and confirm each output line appears within the second its input was fed, which tells us stdout is not block-buffered under `mentl run`. Note the exact behavior at EOF: `read_stdin_line` returns an empty string both at EOF and on an empty line, and the director never sends an empty line, so an empty string is the stop. Report what you saw.

## Probe two, the claims

A `decide(reading, state)` declared `with !Alloc + !Network + !Filesystem` whose body uses a refinement and a `<~ delay(1)` line for the previous reading, in the maker shape of `examples/pulse/course/09-learn.mn`, accepted by `mentl check`. Then the same program with an `effect Net { fetch(url: String) -> String }` and a `fetch` inside `decide`, refused by `mentl check` with `E_EffectMismatch` naming the path. Capture the exact text of `mentl audit` and `mentl why` on the accepted program: the other side designs a two-column CAN/CANNOT card from their shapes.

## station.mn, the controller

Reads C1e lines, writes C2 lines, one decision on the same line as its reading.

**Types.** `type GridHz = Float where 55.0 < self && self < 65.0`. `type SpinW = Int where -100000 <= self && self <= 100000`. `type PulseW = Int where -300000 <= self && self <= 300000`. `type Soc = Int where 0 <= self && self <= 1000`. Every command the program writes passes through these, so the compiler is what keeps each machine under its rating.

**The Station, modeled from Torus's published figures and said so in the head comment.** Spin: 100 kW, 10 kWh (10C, a six-minute full discharge), response under 250 ms. Pulse: 300 kW, 1,200 kWh (four hours at full power). They start at 94 percent and 62 percent state of charge. The facility behind the meter draws 300 kW in rush hours and 200 kW otherwise.

**The maker shape.** The station is minted once in `main`, its state on `<~` lines inside the maker (state of charge of each, the previous `hz_fast`, the EVENT timer, the running mean of `level_db`), exactly as `learner(mu)` in lesson 09 owns its lines, so `decide` stays `!Alloc` and no line is shared across callers. `decide` is `with !Alloc + !Network + !Filesystem`.

**Fast band, Spin, on `hz_fast`.** A deadband of 36 mHz around 60.000: inside it Spin commands 0. Beyond it, output proportional to the deviation, reaching the full 100 kW at 200 mHz past the deadband, discharging when the frequency is low and charging when high. `|rocof| > 0.10 Hz/s` enters EVENT with full Spin in the direction of the deviation; EVENT is left when `|rocof| < 0.05`, held at least 2 s and at most 10 s, so the mode never chatters at the threshold, except that EVENT also holds for as long as the deviation keeps Spin above half its rating (past 136 mHz), so a deep fall stays an event until the grid comes back. Spin's energy bounds it: at 100 kW the 10 kWh is six minutes; when the band is calm Spin recharges from Pulse at 20 kW until full. Mode EVENT while the timer runs, else GRID when Spin is idle.

**Slow band, Pulse, on `rush`, `hour_local` and `clean`.** `rush == 1` discharges Pulse at its full 300 kW across the window (four hours at full power is its whole 1,200 kWh), bounded by state of charge; mode RUSH. Outside the window, the six cleanest hours (highest `clean`) charge Pulse at 150 kW until it is 95 percent full. Pulse never moves on the fast band, except to refill Spin at 20 kW when the band is calm.

**Island, on `level_db` and the nulls.** The running mean of `level_db` over the last ten seconds, frozen while the hum is gone, is the reference. A line 30 dB under it, or a null reading, for two consecutive lines, is the hum gone: mode ISLAND. In ISLAND, Spin supplies the first two seconds and Pulse then carries the facility (300 kW in rush hours, 200 kW otherwise); frequency rules are suspended. The level returning within 10 dB of the reference with real readings for two lines leaves ISLAND.

A Python stand-in with exactly these rules lives in `director.py` (`StubController`) so the page could be built before your program lands; it never runs on stage. Where your reading of the rules and the stub's differ, the stub is the reference for numbers and the brief for intent; say so if you change either.

**Reasons.** Every mode names its rule and the number in words with milli-units, as above. GRID inside the deadband says "within 36 mHz of 60, nothing to do".

**Acceptance, each a run whose output you read.** `mentl check examples/grid/station.mn` clean; `mentl fmt --check` clean. `mentl run examples/grid/station.mn < samples/ear_event.ndjson` (enriched) prints EVENT on the line where `rocof` first crosses 0.10, with the reason naming it, and leaves EVENT between 2 and 10 s later. `< samples/ear_island.ndjson` prints ISLAND within two lines of the level drop. `< samples/ear_hum.ndjson` prints GRID with `spin_w` 0 while `hz_fast` sits inside the deadband.

## station-leak.mn, the refusal twin

`station.mn` with one addition: `effect Net { fetch(url: String) -> String }` and a `fetch("https://api.eia.gov/price")` inside `decide`, used to scale the slow band by price. Plausible code a reasonable engineer would write. `mentl check examples/grid/station-leak.mn` must refuse with `E_EffectMismatch` naming the path from `decide` to `fetch`. The other side captures the text; you only make sure it refuses and the path is named.

## listen.mn, the learner

The one-coefficient predictor on the 480 Hz decimated hum (`samples/hum_480.txt`, one float per line on stdin). A pure sinusoid obeys `x[n] = a * x[n-1] - x[n-2]` with `a = 2 cos(omega)`, so one coefficient carries the frequency. Learn `a` the way lesson 09 learns its filter coefficient: the error `e = x - (a * x1 - x2)` computed by the chain itself, the step `d(e * e)` under `~> grad(a)`, `a` pinned `f64` because the precision of `acos(a / 2)` near 60 Hz at 480 Hz needs it. Print, once per 480 input lines, `acos(a / 2) * 480 / (2 * pi)` in milli-units as `{"hz_learned_m":59984}`. Acceptance: agrees with the ear's `hz` within 3 mHz on the recorded hum, and with the tone sample within 2 mHz.

## predict.mn, the load predictor

Twenty-four parameters, one per hour of the day, learned online from the PACE demand series (`data/pace.json`'s seven days, which the other side will also hand you as a flat `samples/pace_hours.txt`, one `hour demand` pair per line), with derived gradients under `~> grad`, `!Alloc` held on the step. Print the four highest contiguous learned hours as `{"window":[17,21]}`. Acceptance: within one hour of the window EIA's own day-ahead forecast gives.

## score.mn, the piece

Sixteen seconds at 48 kHz stereo in the manner of `examples/wasatch/inversion.mn`: the drone's pitch follows the recorded hum's frequency (from `samples/ear_hum.ndjson`, read as a module the way Wasatch reads its readings), the swell follows the PACE day's demand, each EVENT in `samples/ear_event.ndjson` is a struck tone, the ISLAND is a silence. `mentl run examples/grid/score.mn > score.wav`. The per-sample path `!Alloc + !Network + !Filesystem`, as Wasatch's is.

## The resume recording

The controller persisted mid-stream with `lib/persist` and resumed with `mentl resume`, continuing from the same tick with the same state of charge. Thirty seconds of terminal, captured with `script` or `asciinema` if present, else a plain text log of the commands and their output. Say honestly what did not restore (the stdin position, per persist.mn's own limits).

## The agent transcript

With `mentl mcp` registered through `.mcp.json`, ask a coding agent to add a price lookup to `station.mn` so the slow band follows prices. Capture the proposal and the gate's answer: `REFUSED` with the claim and the span. Keep the exact prompt so it can be run live in a judge's question.

## What to send back

The paths of the programs on main, the commands you ran, their output pasted whole, and anything in this brief that turned out wrong about the language. Short messages, as each piece lands; the other side is building the ear, the director, the page and the decks against this brief in parallel.
