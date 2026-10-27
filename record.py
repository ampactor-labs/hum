#!/usr/bin/env python3 -I
"""Records the bundled session: the director runs the real controller on the
given source, the clock is set to tomorrow's noon for the rush hour, the real
event replays, the hum dies, and the session file lands as
sessions/default.ndjson, which the page plays wherever no director answers.

    python3 -I record.py                 # on the tone sample, no hardware
    python3 -I record.py --mode live     # the guitar on the interface
    python3 -I record.py --mode wav --wav samples/hum_home.wav

About five minutes. Nothing else should touch port 8787 while it runs.
"""
import glob, json, os, signal, shutil, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
mode = args[args.index("--mode") + 1] if "--mode" in args else "sample"
extra = []
if "--wav" in args:
    extra += ["--wav", args[args.index("--wav") + 1]]
if mode == "sample":
    extra += ["--sample", os.path.join(HERE, "samples", "ear_tone.ndjson")]
cmd = [sys.executable, "-I", os.path.join(HERE, "director.py"), "--mode", mode, "--port", "8787",
       "--mentl-dir", os.environ.get("MENTL_DIR", os.path.expanduser("~/mentl")),
       "--mentl-bin", os.environ.get("MENTL_BIN", "mentl")] + extra
before = set(glob.glob(os.path.join(HERE, "sessions", "*.ndjson")))
# The director and everything it spawns share one process group, so the end is one signal.
proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def state():
    return json.load(urllib.request.urlopen("http://127.0.0.1:8787/state.json", timeout=1))


def cmd_(q):
    urllib.request.urlopen("http://127.0.0.1:8787/cmd?" + q, timeout=1).read()


def now(s):
    return s.get("now") or {}


def wait(pred, secs):
    for _ in range(int(secs * 4)):
        time.sleep(0.25)
        try:
            s = state()
            if pred(s):
                return s
        except Exception:
            pass
    return None


t0 = time.time()


def log(m):
    print(f"{time.time() - t0:6.1f}s  {m}", flush=True)


try:
    s = wait(lambda s: now(s).get("mode") and now(s).get("hz") is not None, 90)
    log("first decision: " + (now(s).get("mode") if s else "none; is the source giving lines?"))
    time.sleep(15)
    cmd_("hour=12.5")
    s = wait(lambda s: now(s).get("mode") == "RUSH", 15)
    log("RUSH: " + str(now(s).get("reason") if s else None))
    time.sleep(45)
    cmd_("hour=")
    s = wait(lambda s: now(s).get("hour_set") is None and now(s).get("mode") != "RUSH", 15)
    log("back to now: " + str(now(s).get("mode") if s else None))
    time.sleep(10)
    cmd_("src=replay")
    s = wait(lambda s: now(s).get("mode") == "EVENT", 70)
    log("EVENT: " + str(now(s).get("reason") if s else None) + " | ms " + str(s.get("latency_ms") if s else None))
    s = wait(lambda s: s.get("source") == mode and now(s).get("source") != "replay", 240)
    log("replay ended: " + str(now(s).get("mode") if s else None))
    time.sleep(15)
    cmd_("src=silence")
    s = wait(lambda s: now(s).get("mode") == "ISLAND", 30)
    log("ISLAND: " + str(now(s).get("reason") if s else None))
    time.sleep(20)
    cmd_("src=back")
    s = wait(lambda s: s.get("source") == mode and now(s).get("mode") == "GRID", 40)
    log("back: " + str(now(s).get("mode") if s else None))
    time.sleep(15)
finally:
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)

new = sorted(set(glob.glob(os.path.join(HERE, "sessions", "*.ndjson"))) - before)
if not new:
    sys.exit("no session file was written")
src = new[-1]
rows = [json.loads(l) for l in open(src) if l.strip()]
t_first = rows[0]["ear"]["t"]
seen = {}
for r in rows:
    st = r.get("station") or {}
    m = st.get("mode")
    if m and m not in seen:
        seen[m] = (round(r["ear"]["t"] - t_first, 1), st.get("reason"))
print("lines:", len(rows), "| seconds:", round(rows[-1]["ear"]["t"] - t_first, 1))
for m, (t, why) in seen.items():
    print(f"  {m:7s} first at +{t}s: {why}")
shutil.copyfile(src, os.path.join(HERE, "sessions", "default.ndjson"))
print("copied to sessions/default.ndjson")
