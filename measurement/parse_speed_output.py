#!/usr/bin/env python3
"""parse_speed_output.py -- convert liboqs speed_kem / speed_sig output into the results CSV schema.

liboqs tests/ds_benchmark.h prints a Markdown table with columns
  Operation | Iterations | Total time (s) | Time (us): mean | pop. stdev | CPU cycles: mean | pop. stdev
(timing: gettimeofday wall clock; "CPU cycles" = raw rdtsc on x86, i.e. invariant-TSC ticks on this CPU,
or PMCCNTR_EL0 on ARM when built with OQS_SPEED_USE_ARM_PMU).  speed_kem has no percentiles, so only
mean_us / stdev_us / tsc_ticks_mean are filled; p50/p99 columns are left empty and the notes column says so.
Operation rows are named e.g. keygen / encaps / decaps (speed_kem) and keypair / sign / verify (speed_sig);
algorithm headers appear as lines consisting of the algorithm name alone.

Usage: python3 parse_speed_output.py speed_kem_native.log --label x86_turbo_on_run1 --impl avx2 \
           --library-version 0.16.0 --out results_speed.csv [--host ID] [--hw-class x86_laptop]
"""
import argparse
import csv
import os
import platform
import re
import sys
from datetime import datetime, timezone

COLUMNS = ["timestamp_utc", "host_id", "hardware_class", "cpu_model", "freq_state", "core_pinned", "os",
           "library", "library_version", "implementation", "algorithm", "operation", "message_bytes",
           "n_reps", "warmup_reps", "timing_method", "min_us", "p50_us", "mean_us", "p90_us", "p99_us",
           "max_us", "stdev_us", "tsc_ticks_mean", "source", "notes"]
OPMAP = {"keygen": "keygen", "keypair": "keygen", "encaps": "encaps", "decaps": "decaps",
         "sign": "sign", "verify": "verify", "fullcycletest": "keygen_encaps_decaps"}
ROW = re.compile(r"^\s*([A-Za-z_\- ]+?)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)?\s*\|?\s*([\d.]+)?")
ALG = re.compile(r"^[A-Za-z][A-Za-z0-9\-_+]*$")


def cpu_model():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log")
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--impl", required=True)
    ap.add_argument("--library-version", default="?")
    ap.add_argument("--host", default=platform.node())
    ap.add_argument("--hw-class", default="x86_laptop")
    ap.add_argument("--core", default="taskset")
    a = ap.parse_args()
    base = dict(timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), host_id=a.host,
                hardware_class=a.hw_class, cpu_model=cpu_model(), freq_state=a.label, core_pinned=a.core,
                os=f"{platform.system().lower()}-{platform.release()}", library="liboqs-speed",
                library_version=a.library_version, implementation=a.impl, message_bytes=0, warmup_reps=0,
                timing_method="gettimeofday+rdtsc", min_us="", p50_us="", p90_us="", p99_us="", max_us="",
                source=os.path.basename(a.log),
                notes="mean/pop.stdev only (ds_benchmark.h has no percentiles); "
                      "tsc_ticks_mean = raw rdtsc (invariant TSC ticks, not core cycles)")
    new = not os.path.exists(a.out) or os.path.getsize(a.out) == 0
    out = open(a.out, "a", newline="")
    w = csv.DictWriter(out, fieldnames=COLUMNS)
    if new:
        w.writeheader()
    alg = None
    n = 0
    for line in open(a.log, errors="replace"):
        t = line.strip()
        if not t or t.startswith(("Started", "Ended", "Operation", "---", "|---")):
            continue
        m = ROW.match(t)
        if m and m.group(1).strip().lower() in OPMAP:
            if alg is None:
                print("warning: data row before any algorithm header:", t, file=sys.stderr)
                continue
            w.writerow(dict(base, algorithm=alg, operation=OPMAP[m.group(1).strip().lower()], n_reps=int(m.group(2)),
                            mean_us=m.group(4), stdev_us=m.group(5), tsc_ticks_mean=m.group(6) or ""))
            n += 1
        else:
            # algorithm header: either a bare name or a table row whose first cell is the name and the rest empty,
            # e.g. "ML-KEM-512                          |            |                |  ..."
            cells = [c.strip() for c in t.split("|")]
            if ALG.match(cells[0]) and cells[0].lower() not in OPMAP and all(c == "" for c in cells[1:]):
                alg = cells[0]
    print(f"{n} rows -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
