# HUM contracts

Every process in the demo talks through one of these. They are frozen; a change here is a change in every consumer.

## C1, ear line

NDJSON, one line every 50 ms on the ear's stdout, floats:

```
{"t":1761620000.50,"hz_fast":59.9810,"hz":59.9830,"hz_stft":59.9830,"rocof":-0.004,"thd":3.1,"level_db":-18.5,"harmonic":1,"tuner_hz":59.983,"tuner_cents":-0.8,"scope":[-26,111,205,297,…],"source":"live"}
```

- `t` unix seconds, float. Live: the wall clock at emission. File and synthetic sources: the start wall time plus the sample offset.
- `hz_fast` the three-cycle reading, the one the controller reacts to.
- `hz` the one-second mean of cycle readings, the number on the screen.
- `hz_stft` the two-second spectral peak with quadratic interpolation, the cross-check.
- `rocof` the change of `hz_fast` over the last 100 ms, in Hz per second.
- `thd` percent, harmonics 2 to 10 over the fundamental, from the last two seconds.
- `level_db` the tracked band's level in dBFS.
- `harmonic` the band being tracked, 1, 2 or 3; every frequency above is already divided by it.
- `tuner_hz` and `tuner_cents` the pitch from sonido's tuner kernel, the one in the sonido tuner plugin, with its A4 reference at 427.65 Hz so that 60 Hz is exactly the note B1. `tuner_cents` is the distance from B1: 0 while the grid is in tune, about −20 at 59.3 Hz. Both are `null` while the ear hears no hum.
- `scope` the last three cycles of the input as 96 integers in thousandths of full scale, starting at a rising zero crossing so a steady hum draws in the same place every time. Empty until two seconds have been heard. The director does not pass it to the controller.
- `source` one of `live`, `wav`, `replay`, `tone`, `silence`.

Before the ear has locked (fewer than three cycles), `hz_fast`, `hz`, `hz_stft` and `rocof` are `null` and `level_db` is still real.

## C1e, enriched line

The director adds four fields before the controller sees a line, and the pedal's lines enter here with `"source":"pedal"`:

```
"hour_local":21.4,"rush":0,"clean":0.31,"offset_mhz":2.1
```

- `hour_local` MDT hours as a float; when the director's clock is set (C4 `hour=`), the hour it is set to, and the line also carries `hour_set` with that hour, so a recording replays the set clock.
- `rush` 1 inside the rush-hour window from `data/pace.json`, else 0.
- `clean` the hour's clean share of generation, 0 to 1.
- `offset_mhz` the pickup's bias that the director has subtracted from a live line, in millihertz: the session's mean of the steadied reading minus 60.000. Zero on every other line, and zero for the first five seconds of a live hum.

On a live or pedal line the director also steadies the reading before anyone sees it, because a pickup's reading carries the pickup's own noise: `hz_fast`, `hz` and `tuner_hz` all become the median of the last 1.5 s of `tuner_hz` less `offset_mhz`, `tuner_cents` is recomputed from it, and `rocof` is the slope of that steadied reading over the last second. `hz_stft` stays the ear's own. The 2019 replay, recordings, samples and the tone pass through untouched, so their timing stays as the ear measured it.

The director never sends an empty line.

## C2, station line

NDJSON from the controller, one per input line, written on the same line as its reading. Integers in milli-units, strings for words:

```
{"t":1761620000.50,"mode":"EVENT","spin_w":100000,"pulse_w":0,"spin_soc_m":940,"pulse_soc_m":620,"reason":"falling at 129 mHz per second, past 100"}
```

- `t` the reading's own `t`, copied as the text it arrived as (the controller converts no floats).
- `mode` one of `GRID`, `EVENT`, `RUSH`, `ISLAND`.
- `spin_w`, `pulse_w` watts, positive is discharge into the facility, negative is charge.
- `spin_soc_m`, `pulse_soc_m` state of charge in thousandths.
- `reason` one sentence in words with milli-units, naming the rule and the number that fired it.

## C3, state snapshot

`state.json`, rewritten atomically by the director every 250 ms, the only thing the page reads:

```
{
  "now": { ...the last C1e line..., ...the last C2 line... },
  "trace_fast": [[t, hz_fast], ...],        60 s at 20 Hz
  "trace": [[t, hz], ...],                  10 min at 2 Hz
  "station_trace": [[t, spin_w, pulse_w, mode], ...],   10 min at 2 Hz
  "ledger": { "events": 3, "kwh_moved": 412.0, "spin_cycles": 2.0, "pulse_cycles_saved": 0.8 },
  "pace": { "today": [...24...], "tomorrow": [...24...], "forecast_today": [...], "forecast_tomorrow": [...],
            "window": [17, 21], "clean": [...24...], "as_of": "2026-10-27T14:44Z", "forecast_source": "eia-day-ahead | seven-day-mean" },
  "learned": { "hz": 59.984 },
  "source": "live", "source_label": "guitar, this room",
  "offset_mhz": 2.1,
  "latency_ms": 48,
  "clock": "21:47:03 MDT"
}
```

## C4, director commands

- `GET /cmd?src=live|wav|replay|island|pedal|silence` switches the ear's input or the line source and answers `200 ok`.
- `GET /cmd?reset=1` clears the ledger, the traces and the set clock.
- `GET /cmd?hour=12.5` sets the clock the lines carry to tomorrow's half past noon, inside the rush window, so the Station's rush-hour behavior can be shown at any time of day; `GET /cmd?hour=` returns the clock to now.
- `GET /state.json?ts=<ms>` is cache-busted by the page.
- Static files are served from the demo directory on port 8787.

## C5, pedal line

C1 without `hz_stft` and `thd`, with `"source":"pedal"`, over USB CDC at 20 Hz. The director stamps `t` on arrival.

## C6, samples

Produced by the ear under `samples/` and consumed by the controller and the page before any live integration:

- `ear_tone.ndjson` a synthetic hum at 60.000 Hz with a ±20 mHz wobble.
- `ear_hum.ndjson` the user's recorded hum, once it exists.
- `ear_event.ndjson` a disturbance: nadir 59.80 Hz at 8 s, recovery over 40 s.
- `ear_island.ndjson` a hum that cuts to silence at 30 s.
- `hum_480.txt` the tracked band's signal decimated to 480 Hz, one float per line, for the learner.

The `.ndjson` samples are C1 lines, not C1e; a consumer that needs the enrichment adds `hour_local`, `rush`, `clean` and `offset_mhz` itself, or runs them through the director.

## C7, learner line

From `listen.mn` on the 480 Hz stream (`--emit-decimated`, one float per line), once per 480 input lines:

```
{"hz_learned":60.000312}
```

The director puts it in `learned.hz`. The page does not show it, because the learner trails a fast fall.
