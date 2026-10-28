#!/usr/bin/env python3
"""The HUM director starts the ear and the controller, adds the hour and the
grid's state to every line, keeps the state the page reads, and serves the
page. It uses the standard library only.

    python3 -I director.py --mode live|wav|replay|silence|pedal|sample
        [--wav path] [--sample samples/ear_tone.ndjson] [--serial /dev/ttyACM0]
        [--ear ../../target/release/examples/grid_ear] [--capture "arecord -D pipewire -t raw -f FLOAT_LE -r 48000 -c 1 -"]
        [--stub-controller | --mentl-dir ~/mentl --mentl-bin mentl]
        [--port 8787]

Sources feed the ear (`grid_ear`, C1 lines) or stand in for it (the pedal's
serial lines, or a sample file replayed at 20 Hz). Every line is enriched
(C1e: hour_local, rush, clean, offset_mhz, and hour_set when the clock is set), handed to the controller
(`mentl run examples/grid/station.mn`, or the in-process stand-in when Mentl
is not available), and the decision (C2) comes back on the same line. The
director keeps the traces and the ledger, serves `/state.json` (C3) and
`/cmd` (C4) on port 8787, serves the page's files, and records every line to
`sessions/<date>.ndjson` for the page's playback mode.

A source that ends (the replay, a WAV) returns to the source before it. A
process that dies is restarted within a second; the page shows RECONNECTING
meanwhile.
"""

import datetime as dt
import json
import math
import os
import queue
import shlex
import statistics
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_UTC_OFFSET = -6 * 3600  # MDT through 2026-11-01
NOMINAL = 60.0

# The Station, modeled from Torus's published figures and labeled so on the page.
SPIN_W = 100_000
SPIN_WH = 10_000       # 10C: a six-minute full discharge
PULSE_W = 300_000
PULSE_WH = 1_200_000   # four hours
FACILITY_RUSH_W = 300_000
FACILITY_W = 200_000
DEADBAND = 0.036
FULL_AT = 0.200
ROCOF_ENTER = 0.10
ROCOF_LEAVE = 0.05
EVENT_MIN_S = 2.0
EVENT_MAX_S = 10.0
LOST_DB = 30.0
DT = 0.05
REPLAY_FROM_S = 27  # the real event's first fall is at 35 s on its clock

SOURCE_LABELS = {
    "live": "guitar, this room",
    "pedal": "the pedal",
    "wav": "recording",
    "replay": "real event, GB grid 2019-08-09, transposed to 60 Hz",
    "silence": "the hum is cut",
    "sample": "sample file",
}


def log(msg):
    print(f"director: {msg}", file=sys.stderr, flush=True)


def hour_local(t):
    return ((t + LOCAL_UTC_OFFSET) % 86400) / 3600.0


def clock_local(t):
    return (dt.datetime.fromtimestamp(t, dt.timezone.utc) + dt.timedelta(seconds=LOCAL_UTC_OFFSET)).strftime("%H:%M:%S MDT")


class Pace:
    """The day's shape, window and clean share from data/pace.json."""

    def __init__(self, path):
        try:
            self.data = json.load(open(path))
        except Exception as e:
            log(f"no pace.json ({e}); the rush window is 17 to 21 and clean is 0.3")
            self.data = {}
        self.window = self.data.get("window") or [17, 21]
        clean_today = (self.data.get("for_today") or {}).get("clean") or []
        clean_mean = self.data.get("clean_mean") or []
        self.clean = [
            (clean_today[h] if h < len(clean_today) and clean_today[h] is not None else
             clean_mean[h] if h < len(clean_mean) and clean_mean[h] is not None else 0.3)
            for h in range(24)
        ]
        # The six cleanest hours outside the window charge Pulse.
        outside = [h for h in range(24) if not (self.window[0] <= h < self.window[1])]
        self.charge_hours = set(sorted(outside, key=lambda h: -self.clean[h])[:6])

    def rush(self, hour):
        return 1 if self.window[0] <= int(hour) < self.window[1] else 0

    def clean_at(self, hour):
        return self.clean[int(hour) % 24]

    def for_page(self):
        d = self.data
        return {
            "today": d.get("today"), "tomorrow": d.get("tomorrow"),
            "window": self.window, "forecast_source": d.get("forecast_source"),
            "as_of_local": d.get("as_of_local"),
            "demand_today": (d.get("for_today") or {}).get("demand"),
            "forecast_today": (d.get("for_today") or {}).get("forecast"),
            "forecast_tomorrow": (d.get("for_tomorrow") or {}).get("forecast"),
            "shape": d.get("shape"), "clean": self.clean,
            "charge_hours": sorted(self.charge_hours),
        }


class StubController:
    """The brief's rules in Python, so the page can be built before the Mentl
    program lands. The demo runs the Mentl program; this never ships on stage."""

    def __init__(self):
        self.spin_soc = 0.94
        self.pulse_soc = 0.62
        self.event_since = None
        self.level_ref = None
        self.lost_lines = 0
        self.island_since = None
        self.found_lines = 0

    def decide(self, r):
        t = r["t"]
        hz = r.get("hz_fast")
        rocof = r.get("rocof") or 0.0
        level = r.get("level_db", -120.0)
        rush = r.get("rush", 0)
        hour = int(r.get("hour_local", 0))
        clean = r.get("clean", 0.3)
        spin_w = 0
        pulse_w = 0
        mode = "GRID"
        reason = "listening"

        # The level the hum has held, and whether it is gone.
        if self.level_ref is None and level > -100:
            self.level_ref = level
        elif self.level_ref is not None and self.island_since is None and level > -100:
            self.level_ref += (DT / 10.0) * (level - self.level_ref)
        gone = self.level_ref is not None and (level < self.level_ref - LOST_DB or hz is None)
        if self.island_since is None:
            self.lost_lines = self.lost_lines + 1 if gone else 0
            if self.lost_lines >= 2:
                self.island_since = t
        else:
            back = level > self.level_ref - 10 and hz is not None
            self.found_lines = self.found_lines + 1 if back else 0
            if self.found_lines >= 2:
                self.island_since = None
                self.found_lines = 0
                self.lost_lines = 0

        if self.island_since is not None:
            mode = "ISLAND"
            load = FACILITY_RUSH_W if rush else FACILITY_W
            if t - self.island_since < 2.0 and self.spin_soc > 0.05:
                spin_w = min(SPIN_W, load)
                pulse_w = load - spin_w
                reason = f"the hum is gone, {int(self.level_ref - level) if self.level_ref else 0} dB under its average: Spin carries the first seconds"
            else:
                pulse_w = min(PULSE_W, load) if self.pulse_soc > 0.02 else 0
                reason = f"the hum is gone: Pulse carries {load // 1000} kW, {self.pulse_soc * PULSE_WH / max(load, 1):.1f} h left"
        elif hz is None:
            reason = "listening"
        else:
            d = hz - NOMINAL
            # EVENT: entered on the rate of fall, left on its calming, held 2 to 10 s.
            if self.event_since is None and abs(rocof) > ROCOF_ENTER:
                self.event_since = t
            elif self.event_since is not None:
                held = t - self.event_since
                deep = abs(d) > DEADBAND + FULL_AT / 2  # Spin above half its rating: still the event
                if (held >= EVENT_MAX_S and not deep) or (held >= EVENT_MIN_S and abs(rocof) < ROCOF_LEAVE and not deep):
                    self.event_since = None
            if self.event_since is not None:
                mode = "EVENT"
                direction = -1 if (d < 0 or (d == 0 and rocof < 0)) else 1
                spin_w = -direction * SPIN_W if self.spin_soc > 0.05 else 0
                reason = f"falling at {int(abs(rocof) * 1000)} mHz per second, past {int(ROCOF_ENTER * 1000)}" if rocof < 0 else f"rising at {int(abs(rocof) * 1000)} mHz per second, past {int(ROCOF_ENTER * 1000)}"
            elif abs(d) > DEADBAND:
                frac = min(1.0, (abs(d) - DEADBAND) / FULL_AT)
                spin_w = int(-math.copysign(frac * SPIN_W, d)) if self.spin_soc > 0.05 else 0
                reason = f"{int(abs(d) * 1000)} mHz {'low' if d < 0 else 'high'}, past the 36 mHz band; Spin at {int(frac * 100)} percent"
            else:
                reason = "within 36 mHz of 60, nothing to do"
                if self.spin_soc < 0.94:
                    spin_w = -20_000
                    reason = "within 36 mHz of 60; Spin refilling from Pulse"
            # The slow band.
            if rush and self.pulse_soc > 0.02:
                pulse_w = PULSE_W
                if mode == "GRID":
                    mode = "RUSH"
                    reason = f"rush hour, hour {hour} of {pace.window[0]} to {pace.window[1]}; Pulse carries the building"
            elif hour in pace.charge_hours and self.pulse_soc < 0.95:
                pulse_w = -150_000
                if mode == "GRID" and reason.startswith("within"):
                    reason = f"clean hour ({int(clean * 100)} percent clean); Pulse charging"
            if spin_w < 0:
                pulse_w += -spin_w  # Spin refills from Pulse

        # Energy.
        self.spin_soc = min(1.0, max(0.0, self.spin_soc - spin_w * DT / 3600.0 / SPIN_WH))
        self.pulse_soc = min(1.0, max(0.0, self.pulse_soc - pulse_w * DT / 3600.0 / PULSE_WH))
        return {
            "t_ms": int(round(t * 1000)), "mode": mode,
            "spin_w": int(spin_w), "pulse_w": int(pulse_w),
            "spin_soc_m": int(self.spin_soc * 1000), "pulse_soc_m": int(self.pulse_soc * 1000),
            "reason": reason,
        }


class Learner:
    """`listen.mn` on the ear's decimated stream: the third estimator, learned.

    The ear writes the tracked band at 480 Hz to a file; `tail -F` follows it
    into `mentl run listen.mn`, whose stdout is one `{"hz_learned_m":59984}`
    per second. Nothing here runs unless the program exists."""

    def __init__(self, mentl_bin, program, decimated_path, state):
        self.cmd = ["sh", "-c", f"tail -n +1 -F {shlex.quote(decimated_path)} | {shlex.quote(mentl_bin)} run {shlex.quote(program)}"]
        self.state = state
        self.proc = None
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while True:
            try:
                log("learner: " + " ".join(self.cmd))
                self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, text=True, bufsize=1)
                for line in self.proc.stdout:
                    try:
                        d = json.loads(line.strip())
                    except json.JSONDecodeError:
                        continue
                    if "hz_learned" in d:
                        with self.state.lock:
                            self.state.learned["hz"] = float(d["hz_learned"])
            except Exception as e:
                log(f"learner: {e}")
            time.sleep(2.0)


class MentlController:
    """`mentl run examples/grid/station.mn`: lines in, decisions out."""

    def __init__(self, mentl_bin, mentl_dir):
        self.cmd = [mentl_bin, "run", os.path.join(mentl_dir, "examples", "grid", "station.mn")]
        self.proc = None
        self.q = queue.Queue()
        self.start()

    def start(self):
        log("controller: " + " ".join(self.cmd))
        self.proc = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        threading.Thread(target=self._reader, args=(self.proc,), daemon=True).start()

    def _reader(self, proc):
        for line in proc.stdout:
            self.q.put(line.strip())
        self.q.put(None)

    def decide(self, r):
        if self.proc.poll() is not None:
            log("controller exited; restarting")
            self.start()
        try:
            # The scope trace is for the page; the controller decides from the numbers.
            line = {k: v for k, v in r.items() if k != "scope"}
            self.proc.stdin.write(json.dumps(line, separators=(",", ":")) + "\n")
            self.proc.stdin.flush()
            line = self.q.get(timeout=2.0)
            if line is None:
                return None
            return json.loads(line)
        except Exception as e:
            log(f"controller: {e}")
            return None


class Source:
    """Lines from the ear process, the pedal's serial port or a sample file."""

    def __init__(self, mode, opts):
        self.mode = mode
        self.opts = opts
        self.q = queue.Queue()
        self.procs = []
        self.stop_flag = False
        self.ended = False
        self.started = time.time()
        self.locked = False
        threading.Thread(target=self._run, daemon=True).start()

    def warming_up(self, r):
        """A fresh ear's first unlocked lines are its warm-up, not the hum dying;
        they are withheld for up to 1.5 s. Silence is the hum dying by request."""
        if self.locked or self.mode == "silence":
            return False
        if r.get("hz_fast") is not None or time.time() - self.started > 1.5:
            self.locked = True
            return False
        return True

    def _spawn_ear(self, args, stdin=None):
        cmd = [self.opts.ear] + args
        if self.opts.decimated:
            cmd += ["--emit-decimated", self.opts.decimated]
        log("ear: " + " ".join(cmd))
        return subprocess.Popen(cmd, stdin=stdin, stdout=subprocess.PIPE, text=True, bufsize=1)

    def _run(self):
        o = self.opts
        try:
            if self.mode == "sample":
                path = o.sample
                for line in open(path):
                    if self.stop_flag:
                        return
                    line = line.strip()
                    if line:
                        d = json.loads(line)
                        d["t"] = time.time()
                        self.q.put(json.dumps(d))
                    time.sleep(DT)
                self.ended = True
                return
            if self.mode == "pedal":
                with open(o.serial, "r", buffering=1) as f:
                    for line in f:
                        if self.stop_flag:
                            return
                        line = line.strip()
                        if line.startswith("{"):
                            d = json.loads(line)
                            d["t"] = time.time()
                            d["source"] = "pedal"
                            self.q.put(json.dumps(d))
                self.ended = True
                return
            if self.mode == "live":
                cap = subprocess.Popen(shlex.split(o.capture), stdout=subprocess.PIPE)
                ear = self._spawn_ear(["--stdin-f32", "--source", "live"], stdin=cap.stdout)
                self.procs = [cap, ear]
            elif self.mode == "wav":
                ear = self._spawn_ear(["--wav", o.wav, "--realtime", "--source", "wav"])
                self.procs = [ear]
            elif self.mode == "replay":
                # The replay starts eight seconds before the first fall, so a key
                # press shows the event, not a minute of calm before it.
                seconds = 70
                try:
                    rows = [l.split(",") for l in open(o.event) if l.strip() and not l.startswith("#")]
                    seconds = int(float(rows[-1][0])) + 2 - REPLAY_FROM_S
                except Exception:
                    pass
                ear = self._spawn_ear(["--replay", o.event, "--from", str(REPLAY_FROM_S), "--seconds", str(seconds), "--realtime", "--source", "replay"])
                self.procs = [ear]
            elif self.mode == "silence":
                ear = self._spawn_ear(["--silence", "--seconds", "3600", "--realtime", "--source", "silence"])
                self.procs = [ear]
            else:
                raise ValueError(self.mode)
            for line in ear.stdout:
                if self.stop_flag:
                    break
                self.q.put(line.strip())
        except Exception as e:
            log(f"source {self.mode}: {e}")
        finally:
            self.ended = True
            self.stop()

    def stop(self):
        self.stop_flag = True
        for p in self.procs:
            try:
                p.terminate()
            except Exception:
                pass


class State:
    def __init__(self, pace, opts):
        self.pace = pace
        self.opts = opts
        self.lock = threading.Lock()
        self.now = {}
        self.trace_fast = []
        self.trace = []
        self.station_trace = []
        self.ledger = {"events": 0, "kwh_moved": 0.0, "spin_cycles": 0.0, "pulse_cycles_saved": 0.0}
        self.tuner_hist = []     # the last STEADY_WINDOW tuner readings of a live hum
        self.median_hist = []    # the last SLOPE_WINDOW steadied readings, with their times
        self.bias_sum = 0.0      # the session's mean of the steadied reading minus 60 Hz
        self.bias_n = 0
        self.bias_mhz = 0.0
        self.latency_ms = None
        self.last_mode = "GRID"
        self.learned = {}
        self.hour_set = None  # the hour the lines carry when the clock is set, tomorrow's noon on a key
        self.source = opts.mode
        self.connected = False
        self.line_count = 0
        self.session = None
        os.makedirs(os.path.join(HERE, "sessions"), exist_ok=True)
        self.session = open(os.path.join(HERE, "sessions", time.strftime("%Y-%m-%d_%H%M") + ".ndjson"), "a")

    def enrich(self, r):
        t = r["t"]
        h = hour_local(t) if self.hour_set is None else self.hour_set
        r["hour_local"] = round(h, 3)
        if self.hour_set is not None:
            r["hour_set"] = self.hour_set
        r["rush"] = self.pace.rush(h)
        r["clean"] = self.pace.clean_at(h)
        live = r.get("source") in ("live", "pedal", "wav")
        if live:
            self.steady(r)
        r["offset_mhz"] = self.bias_mhz if live else 0.0
        return r

    # A pickup's reading of the hum carries the pickup's own noise. On a 60 s
    # recording of a guitar held near a 12 V adapter (2026-10-28), the ear's
    # 100 ms reading wandered by tens of millihertz and jumped by hundreds,
    # while the grid itself moves by a few, so the controller read the noise
    # as the grid falling and the flywheel pushed in 78 percent of readings.
    # A live line's frequency (and a recording's, which came through the
    # same pickup) is therefore the median of the last 1.5 s of
    # sonido's tuner readings, less the session's mean of that median, which
    # is the pickup's bias against the grid's long-run average of exactly
    # 60 Hz. The rate of change is the slope of the steadied reading over
    # the last second. On the same recording the flywheel then pushed in
    # 2 percent of readings. The 2019 replay, recordings and samples are not
    # touched, so their timing stays as measured. The bias is applied only
    # after BIAS_AFTER readings, and the history starts over whenever the hum
    # is lost, so an island still shows within half a second.
    STEADY_WINDOW = 30   # readings, 1.5 s at 20 per second
    SLOPE_WINDOW = 20    # readings, 1 s
    BIAS_AFTER = 100     # readings, 5 s

    def steady(self, r):
        v = r.get("tuner_hz")
        if v is None or r.get("hz_fast") is None:
            self.tuner_hist.clear()
            self.median_hist.clear()
            return
        self.tuner_hist.append(v)
        del self.tuner_hist[:-self.STEADY_WINDOW]
        m = statistics.median(self.tuner_hist)
        self.bias_sum += m - NOMINAL
        self.bias_n += 1
        bias = self.bias_sum / self.bias_n if self.bias_n >= self.BIAS_AFTER else 0.0
        self.bias_mhz = round(1000.0 * bias, 1)
        hz = round(m - bias, 4)
        self.median_hist.append((r["t"], hz))
        del self.median_hist[:-self.SLOPE_WINDOW]
        (t0, h0), (t1, h1) = self.median_hist[0], self.median_hist[-1]
        # Until a full second of steadied readings exists, the slope is not reported: the first readings after a hum appears are the roughest.
        r["rocof"] = round((h1 - h0) / (t1 - t0), 4) if len(self.median_hist) == self.SLOPE_WINDOW and t1 > t0 else 0.0
        r["hz_fast"] = hz
        r["hz"] = hz
        r["tuner_hz"] = hz
        r["tuner_cents"] = round(1200.0 * math.log2(hz / NOMINAL), 1)

    def record(self, r, d, latency_ms):
        with self.lock:
            self.line_count += 1
            self.connected = True
            if d is not None:
                mode = d["mode"]
                if mode == "EVENT" and self.last_mode != "EVENT":
                    self.ledger["events"] += 1
                    self.latency_ms = latency_ms
                self.last_mode = mode
                if d["pulse_w"] > 0 and r.get("rush"):
                    self.ledger["kwh_moved"] += d["pulse_w"] * DT / 3600.0 / 1000.0
                if d["spin_w"] > 0:
                    kwh = d["spin_w"] * DT / 3600.0 / 1000.0
                    self.ledger["spin_cycles"] += kwh / (SPIN_WH / 1000.0)
                    self.ledger["pulse_cycles_saved"] += kwh / (PULSE_WH / 1000.0)
            merged = dict(r)
            if d:
                merged.update(d)
            self.now = merged
            self.trace_fast.append([round(r["t"], 2), r.get("hz_fast")])
            if len(self.trace_fast) > 1200:
                del self.trace_fast[: len(self.trace_fast) - 1200]
            if self.line_count % 10 == 0:
                self.trace.append([round(r["t"], 1), r.get("hz")])
                self.station_trace.append([round(r["t"], 1), d["spin_w"] if d else 0, d["pulse_w"] if d else 0, d["mode"] if d else "GRID"])
                if len(self.trace) > 1200:
                    del self.trace[: len(self.trace) - 1200]
                    del self.station_trace[: len(self.station_trace) - 1200]
            if self.session:
                row = {"ear": r, "station": d, "ms": latency_ms}
                if self.learned.get("hz") is not None:
                    row["learned"] = round(self.learned["hz"], 4)
                self.session.write(json.dumps(row, separators=(",", ":")) + "\n")
                if self.line_count % 20 == 0:
                    self.session.flush()

    def reset(self):
        with self.lock:
            self.hour_set = None
            self.trace_fast.clear()
            self.trace.clear()
            self.station_trace.clear()
            self.ledger = {"events": 0, "kwh_moved": 0.0, "spin_cycles": 0.0, "pulse_cycles_saved": 0.0}
            self.latency_ms = None

    def snapshot(self):
        with self.lock:
            t = self.now.get("t", time.time())
            return json.dumps({
                "now": self.now,
                "trace_fast": self.trace_fast,
                "trace": self.trace,
                "station_trace": self.station_trace,
                "ledger": {k: round(v, 3) if isinstance(v, float) else v for k, v in self.ledger.items()},
                "pace": self.pace.for_page(),
                "learned": self.learned,
                "source": self.source,
                "source_label": SOURCE_LABELS.get(self.source, self.source),
                "offset_mhz": self.now.get("offset_mhz", 0.0),
                "latency_ms": self.latency_ms,
                "connected": self.connected,
                "clock": clock_local(time.time()),
                "station": {"spin_w": SPIN_W, "spin_wh": SPIN_WH, "pulse_w": PULSE_W, "pulse_wh": PULSE_WH,
                             "label": "Spin, a flywheel, handles fast changes; Pulse, a battery, carries load for hours. Modeled from Torus's published figures: 100 kW of Spin for six minutes, 300 kW of Pulse for four hours. Simulated."},
            }, separators=(",", ":"))


class Director:
    def __init__(self, opts):
        self.opts = opts
        self.pace = Pace(os.path.join(HERE, "data", "pace.json"))
        global pace
        pace = self.pace
        self.state = State(self.pace, opts)
        if opts.stub_controller:
            self.controller = StubController()
            log("controller: in-process stub (development only)")
        else:
            self.controller = MentlController(opts.mentl_bin, opts.mentl_dir)
        # The learned estimator, when its program and the ear's decimated stream exist.
        # A stream left by an earlier run is not this run's hum: it is removed first.
        listen = os.path.join(opts.mentl_dir, "examples", "grid", "listen.mn")
        if os.path.exists(listen) and opts.decimated:
            try:
                os.remove(opts.decimated)
            except FileNotFoundError:
                pass
            self.learner = Learner(opts.mentl_bin, listen, opts.decimated, self.state)
        self.source = None
        self.previous_mode = opts.mode
        self.requested = None
        self.switch(opts.mode, remember=False)

    def switch(self, mode, remember=True):
        if self.source:
            if remember and self.source.mode not in ("replay", "silence"):
                self.previous_mode = self.source.mode
            self.source.stop()
        log(f"source: {mode}")
        self.state.source = mode
        self.state.connected = False
        with self.state.lock:
            self.state.learned = {}  # the learner's reading belonged to the source that ends here
        self.source = Source(mode, self.opts)

    def request(self, mode):
        self.requested = mode

    def loop(self):
        last_snapshot = 0.0
        while True:
            if self.requested:
                mode = self.requested
                self.requested = None
                if mode == "back":
                    mode = self.previous_mode
                self.switch(mode)
            try:
                line = self.source.q.get(timeout=0.25)
            except queue.Empty:
                line = None
                if self.source.ended:
                    # A replay or a recording that ran out returns to what was before it.
                    nxt = self.previous_mode if self.source.mode in ("replay", "wav", "sample", "silence") else self.source.mode
                    if nxt == self.source.mode:
                        time.sleep(1.0)
                    self.switch(nxt, remember=False)
                else:
                    self.state.connected = False
            if line:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if self.source.warming_up(r):
                    continue
                r = self.state.enrich(r)
                sent = time.time()
                d = self.controller.decide(r)
                latency_ms = round((time.time() - sent) * 1000, 1)
                self.state.record(r, d, latency_ms)
            if time.time() - last_snapshot > 1.0:
                last_snapshot = time.time()
                try:
                    tmp = os.path.join(HERE, "state.json.tmp")
                    with open(tmp, "w") as f:
                        f.write(self.state.snapshot())
                    os.replace(tmp, os.path.join(HERE, "state.json"))
                except Exception as e:
                    log(f"snapshot: {e}")


class Handler(SimpleHTTPRequestHandler):
    director = None

    def __init__(self, *a, **k):
        super().__init__(*a, directory=HERE, **k)

    def log_message(self, *a):
        pass

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/state.json":
            body = self.director.state.snapshot().encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if url.path == "/cmd":
            q = urllib.parse.parse_qs(url.query, keep_blank_values=True)
            if "src" in q:
                self.director.request(q["src"][0])
            if "reset" in q:
                self.director.state.reset()
            if "hour" in q:
                # `hour=12.5` sets the clock the lines carry to tomorrow's half past noon; `hour=` returns it to now.
                v = q["hour"][0].strip()
                self.director.state.hour_set = float(v) if v else None
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class Opts:
    pass


def parse(argv):
    o = Opts()
    o.mode = "sample"
    o.wav = None
    o.sample = os.path.join(HERE, "samples", "ear_tone.ndjson")
    o.serial = "/dev/ttyACM0"
    o.event = os.path.join(HERE, "data", "event.csv")
    o.ear = os.path.join(HERE, "ear", "target", "release", "grid_ear")
    o.capture = "arecord -D pipewire -t raw -f FLOAT_LE -r 48000 -c 1 -"
    o.stub_controller = False
    o.mentl_dir = os.environ.get("MENTL_DIR", os.path.expanduser("~/mentl"))
    o.mentl_bin = os.environ.get("MENTL_BIN", "mentl")
    o.port = 8787
    o.decimated = os.path.join(HERE, "sessions", "decimated_480.txt")
    i = 0
    while i < len(argv):
        a = argv[i]
        def val():
            nonlocal i
            i += 1
            return argv[i]
        if a == "--mode": o.mode = val()
        elif a == "--wav": o.wav = val()
        elif a == "--sample": o.sample = val()
        elif a == "--serial": o.serial = val()
        elif a == "--event": o.event = val()
        elif a == "--ear": o.ear = val()
        elif a == "--capture": o.capture = val()
        elif a == "--stub-controller": o.stub_controller = True
        elif a == "--mentl-dir": o.mentl_dir = val()
        elif a == "--mentl-bin": o.mentl_bin = val()
        elif a == "--port": o.port = int(val())
        elif a == "--decimated": o.decimated = val()
        elif a == "--no-decimated": o.decimated = None
        else:
            log(f"unknown argument {a}")
            sys.exit(2)
        i += 1
    return o


pace = None


def main():
    opts = parse(sys.argv[1:])
    director = Director(opts)
    Handler.director = director
    server = ThreadingHTTPServer(("127.0.0.1", opts.port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log(f"serving http://127.0.0.1:{opts.port}/  state at /state.json  commands at /cmd?src=live|wav|replay|silence|pedal|back  hour=12.5|")
    director.loop()


if __name__ == "__main__":
    main()
