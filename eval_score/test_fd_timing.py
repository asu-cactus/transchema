import sys, time, os, signal
sys.path.insert(0, ".")
import pandas as pd
import fdtool.fdtool as fdtool

FD_TIMEOUT = 60

def run_fdtool(df):
    def _handler(signum, frame):
        raise TimeoutError("FD mining exceeded time limit")
    signal.signal(signal.SIGALRM, _handler)
    signal.alarm(FD_TIMEOUT)
    try:
        result = fdtool.main(df)
        signal.alarm(0)
        return result
    except TimeoutError:
        signal.alarm(0)
        return [], [], []

BASE = "/home/asurite.ad.asu.edu/jrtandel/Documents/transchema_main/transchema/autopipeline-benchmarks/github-pipelines"
cases = [
    "length9_13",   # 182 cols, 19,252 rows
    "length1_89",   # 254 cols, 253 rows
    "length6_87",   # 146 cols, 6,194 rows
    "length4_63",   # 522 cols, 29 rows
    "length6_38",   # 128 cols, 4,017 rows
]

for name in cases:
    csv_path = os.path.join(BASE, name, "target.csv")
    print(f"\n--- {name} ---")
    t0 = time.time()
    df = pd.read_csv(csv_path)
    print(f"  Loaded: {len(df):,} rows x {len(df.columns)} cols  ({time.time()-t0:.1f}s)")
    sys.stdout.flush()

    df = df.iloc[:, :52]
    print(f"  After col truncation: {len(df.columns)} cols")
    sys.stdout.flush()
    try:
        t1 = time.time()
        FDs, E, keys = run_fdtool(df)
        elapsed = time.time() - t1
        status = "TIMEOUT (empty)" if elapsed >= 59.5 else "OK"
        print(f"  FD mining: {elapsed:.2f}s  |  FDs found: {len(FDs)}  [{status}]")
    except Exception as ex:
        print(f"  ERROR: {ex}")
    sys.stdout.flush()
