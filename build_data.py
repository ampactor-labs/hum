#!/usr/bin/env python3
"""Build HUM's data files: PacifiCorp East's hours and a real grid event.

    python3 -I build_data.py [--csv eia930.csv] [--out data] [--no-neso]

PACE (PacifiCorp East, the balancing authority Salt Lake City sits in) comes
from EIA-930, two ways that merge:

- The six-month CSV, no key, updated daily about 14:44 UTC:
  https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2026_Jul_Dec.csv
  (passed with --csv, else downloaded). It carries demand, the day-ahead
  demand forecast and the fuel mix by hour, as reported so far.
- The v2 API, when EIA_API_KEY is set in the environment, which has the
  hours reported since the CSV snapshot, including tomorrow's day-ahead
  forecast once the utility files it. Register at eia.gov/opendata; the key
  is free. The key never enters a file and the demo never needs it: this
  script runs before the demo and writes data/pace.json.

The event for the replay is the 9 August 2019 disturbance on the GB grid,
from NESO's open system-frequency dataset (one-second data, open licence),
transposed to a 60 Hz grid per unit and labeled so in the file's first line.
If the download fails, a synthetic event of the same shape is written and
labeled synthetic. Stdlib only.
"""

import csv
import datetime as dt
import io
import json
import os
import sys
import urllib.parse
import urllib.request

EIA_CSV = "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2026_Jul_Dec.csv"
EIA_API = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
EIA_FUEL_API = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
NESO_PACKAGE = "https://api.neso.energy/api/3/action/package_show?id=system-frequency-data"
BA = "PACE"
LOCAL_UTC_OFFSET_HOURS = -6  # MDT; DST ends 2026-11-01

CLEAN_COLUMNS = [
    "Net Generation (MW) from Nuclear",
    "Net Generation (MW) from Hydropower Excluding Pumped Storage",
    "Net Generation (MW) from Solar without Integrated Battery Storage",
    "Net Generation (MW) from Solar with Integrated Battery Storage",
    "Net Generation (MW) from Wind without Integrated Battery Storage",
    "Net Generation (MW) from Wind with Integrated Battery Storage",
    "Net Generation (MW) from Geothermal",
]
FUEL_COLUMNS = CLEAN_COLUMNS + [
    "Net Generation (MW) from Coal",
    "Net Generation (MW) from Natural Gas",
    "Net Generation (MW) from All Petroleum Products",
    "Net Generation (MW) from Pumped Storage",
    "Net Generation (MW) from Battery Storage",
    "Net Generation (MW) from Other Energy Storage",
    "Net Generation (MW) from Unknown Energy Storage",
    "Net Generation (MW) from Other Fuel Sources",
    "Net Generation (MW) from Unknown Fuel Sources",
]


def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "hum-build-data/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def num(s):
    s = (s or "").strip().replace(",", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def local_date_hour(utc_end_text):
    """EIA's 'UTC Time at End of Hour' -> (local date, hour-beginning 0..23)."""
    t = dt.datetime.strptime(utc_end_text.strip(), "%m/%d/%Y %I:%M:%S %p")
    start_local = t + dt.timedelta(hours=LOCAL_UTC_OFFSET_HOURS) - dt.timedelta(hours=1)
    return start_local.date().isoformat(), start_local.hour


def read_csv_rows(text):
    days = {}
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        if row.get("Balancing Authority") != BA:
            continue
        date, hour = local_date_hour(row["UTC Time at End of Hour"])
        d = days.setdefault(date, {"demand": [None] * 24, "forecast": [None] * 24, "clean": [None] * 24})
        d["demand"][hour] = num(row.get("Demand (MW)"))
        d["forecast"][hour] = num(row.get("Demand Forecast (MW)"))
        fuels = [num(row.get(c)) for c in FUEL_COLUMNS]
        total = sum(v for v in fuels if v is not None and v > 0)
        clean = sum(v for c, v in zip(FUEL_COLUMNS, fuels) if c in CLEAN_COLUMNS and v is not None and v > 0)
        d["clean"][hour] = round(clean / total, 3) if total > 0 else None
    return days


def read_api(days, key, start_date):
    """Merge demand (D) and day-ahead forecast (DF) hours from the v2 API."""
    q = {
        "api_key": key,
        "frequency": "hourly",
        "data[0]": "value",
        "facets[respondent][]": BA,
        "start": start_date.isoformat() + "T00",
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": "5000",
    }
    url = EIA_API + "?" + urllib.parse.urlencode(q) + "&facets[type][]=D&facets[type][]=DF"
    payload = json.loads(fetch(url).decode())
    rows = payload.get("response", {}).get("data", [])
    merged = 0
    for r in rows:
        period = r.get("period")  # "2026-10-27T05", UTC, hour beginning
        if not period or r.get("value") is None:
            continue
        t = dt.datetime.strptime(period, "%Y-%m-%dT%H") + dt.timedelta(hours=LOCAL_UTC_OFFSET_HOURS)
        date, hour = t.date().isoformat(), t.hour
        d = days.setdefault(date, {"demand": [None] * 24, "forecast": [None] * 24, "clean": [None] * 24})
        kind = "demand" if r.get("type") == "D" else "forecast"
        d[kind][hour] = float(r["value"])
        merged += 1
    return merged


def best_window(values, width=4):
    """The contiguous `width` hours with the highest sum; (start, end) hour-beginning."""
    best, best_sum = None, None
    for h0 in range(0, 24 - width + 1):
        seg = values[h0 : h0 + width]
        if any(v is None for v in seg):
            continue
        s = sum(seg)
        if best_sum is None or s > best_sum:
            best, best_sum = h0, s
    return [best, best + width] if best is not None else None


def mean_shape(days, dates, key):
    out = []
    for h in range(24):
        vals = [days[d][key][h] for d in dates if d in days and days[d][key][h] is not None]
        out.append(round(sum(vals) / len(vals), 1) if vals else None)
    return out


def build_pace(csv_path, out_dir):
    if csv_path and os.path.exists(csv_path):
        text = open(csv_path, encoding="utf-8", errors="replace").read()
        source = csv_path
    else:
        print("downloading the EIA-930 six-month CSV (about 30 MB)...", file=sys.stderr)
        text = fetch(EIA_CSV, timeout=300).decode("utf-8", errors="replace")
        source = EIA_CSV
    days = read_csv_rows(text)
    api_merged = 0
    key = os.environ.get("EIA_API_KEY")
    if key:
        try:
            api_merged = read_api(days, key, dt.date.today() - dt.timedelta(days=2))
            print(f"EIA API: merged {api_merged} hours", file=sys.stderr)
        except Exception as e:  # the CSV path stands on its own
            print(f"EIA API failed, CSV only: {e}", file=sys.stderr)

    now_local = dt.datetime.utcnow() + dt.timedelta(hours=LOCAL_UTC_OFFSET_HOURS)
    today = now_local.date()
    tomorrow = today + dt.timedelta(days=1)
    dates = sorted(days)
    last7 = [d for d in dates if d < today.isoformat()][-7:]
    shape = mean_shape(days, last7, "demand")
    clean_mean = mean_shape(days, last7, "clean")

    def day(dstr):
        return days.get(dstr, {"demand": [None] * 24, "forecast": [None] * 24, "clean": [None] * 24})

    # The rush-hour window: tomorrow's day-ahead forecast when it exists, else
    # today's, else the seven-day mean shape; the source is named.
    for label, values in (
        ("eia-day-ahead-tomorrow", day(tomorrow.isoformat())["forecast"]),
        ("eia-day-ahead-today", day(today.isoformat())["forecast"]),
        ("seven-day-mean", shape),
    ):
        window = best_window(values)
        if window:
            forecast_source = label
            break
    # Last reported hour, for the as-of stamp.
    reported = [(d, h) for d in dates for h in range(24) if days[d]["demand"][h] is not None]
    last_d, last_h = reported[-1] if reported else (None, None)

    pace = {
        "ba": BA,
        "ba_name": "PacifiCorp East",
        "timezone": "America/Denver (MDT, UTC-6)",
        "as_of_local": f"{last_d} hour {last_h:02d}:00" if last_d else None,
        "built_local": now_local.strftime("%Y-%m-%d %H:%M"),
        "source": {"csv": source, "api_hours_merged": api_merged},
        "today": today.isoformat(),
        "tomorrow": tomorrow.isoformat(),
        "window": window,
        "forecast_source": forecast_source,
        "days": {d: days[d] for d in dates[-8:]},
        "shape": shape,
        "clean_mean": clean_mean,
        "for_today": day(today.isoformat()),
        "for_tomorrow": day(tomorrow.isoformat()),
    }
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "pace.json"), "w") as f:
        json.dump(pace, f, indent=1)
    have_t = sum(v is not None for v in pace["for_today"]["forecast"])
    have_tm = sum(v is not None for v in pace["for_tomorrow"]["forecast"])
    print(
        f"pace.json: {len(dates)} days, last reported {pace['as_of_local']}, "
        f"forecast hours today {have_t}, tomorrow {have_tm}, window {window} from {forecast_source}",
        file=sys.stderr,
    )
    # A flat file for the Mentl predictor: one 'hour demand' pair per line, seven days.
    with open(os.path.join(out_dir, "pace_hours.txt"), "w") as f:
        for d in last7:
            for h in range(24):
                v = days[d]["demand"][h]
                if v is not None:
                    f.write(f"{h} {v:.0f}\n")


def synthetic_event():
    import math

    rows = ["# synthetic event: trip at t=5 s, initial fall 0.20 Hz/s, nadir 59.80 Hz near t=10 s, recovery over 40 s"]
    for i in range(0, 70 * 10 + 1):
        t = i / 10
        if t < 5:
            hz = 60.0
        else:
            u = t - 5
            if u <= 5:
                hz = 60.0 - 0.20 * (1 - math.exp(-u / 1.0)) / (1 - math.exp(-5.0))
            else:
                hz = 59.80 + 0.17 * (1 - math.exp(-(u - 5) / 12))
        rows.append(f"{t:.1f},{hz:.4f}")
    return "\n".join(rows) + "\n"


def build_event(out_dir, allow_neso=True):
    path = os.path.join(out_dir, "event.csv")
    if allow_neso:
        try:
            pkg = json.loads(fetch(NESO_PACKAGE, timeout=60).decode())
            resources = pkg["result"]["resources"]
            cand = [r for r in resources if "2019" in (r.get("name", "") + r.get("url", "")) and ("8" in r.get("name", "") or "aug" in r.get("name", "").lower())]
            # Prefer a CSV whose name holds both 2019 and August.
            cand = [r for r in cand if r.get("url", "").lower().endswith(".csv")] or cand
            if not cand:
                raise RuntimeError("no 2019 August resource listed")
            url = cand[0]["url"]
            local_zip = os.environ.get("NESO_ZIP")
            if local_zip and os.path.exists(local_zip):
                raw = open(local_zip, "rb").read()
            else:
                print(f"NESO: fetching {cand[0].get('name')} ...", file=sys.stderr)
                raw = fetch(url, timeout=600)
            if raw[:2] == b"PK":
                import zipfile

                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    member = next(n for n in z.namelist() if n.lower().endswith(".csv"))
                    raw = z.read(member)
            text = raw.decode("utf-8", errors="replace")
            reader = csv.reader(io.StringIO(text))
            header = next(reader)
            ti = next(i for i, h in enumerate(header) if "dtm" in h.lower() or "time" in h.lower())
            fi = next(i for i, h in enumerate(header) if h.lower().strip() in ("f", "frequency") or "freq" in h.lower())
            # The file's clock is BST (+0100): the Hornsea and Little Barford
            # trips at 16:52:33, the nadir of 48.8 Hz at 16:53:49, recovery by 16:55.
            start = dt.datetime(2019, 8, 9, 16, 52, 0)
            end = dt.datetime(2019, 8, 9, 16, 55, 0)
            rows = []
            for row in reader:
                try:
                    t = dt.datetime.strptime(row[ti][:19], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        t = dt.datetime.strptime(row[ti][:19], "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        continue
                if start <= t <= end:
                    f = float(row[fi])
                    rows.append(((t - start).total_seconds(), 60.0 * f / 50.0))
            if len(rows) < 150:
                raise RuntimeError(f"only {len(rows)} rows in the window")
            with open(path, "w") as f:
                f.write("# real event: GB grid, 2019-08-09 16:52 to 16:55 BST, the Hornsea and Little Barford trips, NESO open data at 1 s, transposed to 60 Hz per unit\n")
                for t, hz in rows:
                    f.write(f"{t:.0f},{hz:.4f}\n")
            print(f"event.csv: real, {len(rows)} seconds, min {min(h for _, h in rows):.3f} Hz (transposed)", file=sys.stderr)
            return
        except Exception as e:
            print(f"NESO failed, writing the synthetic event: {e}", file=sys.stderr)
    with open(path, "w") as f:
        f.write(synthetic_event())
    print("event.csv: synthetic, labeled", file=sys.stderr)


def main(argv):
    csv_path, out_dir, allow_neso = None, "data", True
    only = None
    i = 0
    while i < len(argv):
        if argv[i] == "--csv":
            i += 1
            csv_path = argv[i]
        elif argv[i] == "--out":
            i += 1
            out_dir = argv[i]
        elif argv[i] == "--no-neso":
            allow_neso = False
        elif argv[i] == "--event-only":
            only = "event"
        elif argv[i] == "--pace-only":
            only = "pace"
        i += 1
    if only != "event":
        build_pace(csv_path, out_dir)
    if only != "pace":
        build_event(out_dir, allow_neso)


if __name__ == "__main__":
    main(sys.argv[1:])
