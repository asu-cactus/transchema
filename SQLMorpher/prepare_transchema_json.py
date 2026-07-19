"""Converts Transchema's flat Auto-Pipeline JSON (list of source/target rows)
into the grouped-by-target format that `auto_pipeline_join.gpt_auto_pipeline`
expects (dict: Target Data Name -> list of rows), so SQLMorpher can run on the
exact same dataset as Transchema without touching Excel files.

The benchmark folders on disk (autopipeline-benchmarks/{benchmark}-pipelines/
length{L}_{id}/) contain every case, but Transchema's metadata JSON
(chatgpt_github_ms.json etc.) only covers a subset of them (e.g. 42/100 for
length1). For any case that exists on disk but is missing from the JSON, we
synthesize the same fields (schema, samples) directly from the CSVs so
SQLMorpher can still build a prompt for it.
"""

import glob
import json
import os
import re
from collections import defaultdict

import pandas as pd

_BENCHMARK_JSON = {
    "github": "chatgpt_github_ms.json",
    "monteprep": "chatgpt_monteprep_ms.json",
}

_BENCHMARK_DIRS = {
    "github": "../autopipeline-benchmarks/github-pipelines",
    "monteprep": "../autopipeline-benchmarks/monteprep-pipelines",
}

_CASE_DIR_RE = re.compile(r"^length(\d+)_(\d+)$")


def read_schema_and_samples(csv_path, n_samples=3):
    """Reads the real column headers + a few sample rows directly from a CSV
    on disk. Used both to synthesize metadata for cases missing from
    Transchema's JSON, and to override that JSON's (sometimes index-column-
    stripped) schema so it always matches exactly what a raw SQL `COPY` of
    the file would see."""
    df = pd.read_csv(csv_path, low_memory=False, nrows=200)
    schema = list(df.columns)
    samples = df.head(n_samples).values.tolist()
    return schema, samples


# Kept as a private alias for backwards compatibility within this module.
_read_schema_and_samples = read_schema_and_samples


def _synthesize_case_rows(length, case_id, case_dir):
    """Builds rows matching the flat-JSON schema for a case found on disk but
    missing from Transchema's metadata JSON, by reading its CSVs directly."""
    target_path = os.path.join(case_dir, "target.csv")
    if not os.path.exists(target_path):
        return []

    target_data_name = f"Target{length}_{case_id}"
    try:
        target_schema, target_samples = _read_schema_and_samples(target_path)
    except Exception:
        return []

    source_paths = sorted(glob.glob(os.path.join(case_dir, "test_*.csv")))
    rows = []
    for i, source_path in enumerate(source_paths):
        try:
            source_schema, source_samples = _read_schema_and_samples(source_path)
        except Exception:
            continue
        rows.append({
            "Target Data Name": target_data_name,
            "Target Data Schema": str(target_schema),
            "Target Data Schema with Types": str(target_schema),
            "Target Data Sample": str(target_samples),
            "Target Data Description": "",
            "Source Data Name": f"Source{length}_{case_id}_{i}",
            "Source Data Schema": str(source_schema),
            "Source Data Schema with Types": str(source_schema),
            "3 Samples of Source Data": str(source_samples),
        })
    return rows


def list_cases_on_disk(benchmark_dir, lengths=None):
    """Lists all (length, case_id) pairs found on disk under benchmark_dir
    (just directory names — cheap, no CSV reads). If `lengths` is given,
    restricts to those length(s)."""
    benchmark_dir = os.path.abspath(benchmark_dir)
    if not os.path.isdir(benchmark_dir):
        return []

    lengths = set(lengths) if lengths is not None else None
    pairs = []
    for entry in sorted(os.listdir(benchmark_dir)):
        match = _CASE_DIR_RE.match(entry)
        if not match:
            continue
        length, case_id = int(match.group(1)), int(match.group(2))
        if lengths is not None and length not in lengths:
            continue
        pairs.append((length, case_id))
    return sorted(pairs)


def build_grouped_json(benchmark="github", transchema_data_dir="../data", cache_dir="."):
    """Returns the path to a grouped JSON file for `benchmark`, building it
    from Transchema's flat JSON if not already cached. This does NOT scan the
    benchmark folders (that would mean reading CSVs across all ~700 cases /
    several GB every time the cache needs rebuilding). Use
    `ensure_cases_available` afterwards to lazily synthesize metadata for only
    the specific case(s) you're about to run."""
    src_name = _BENCHMARK_JSON[benchmark]
    src_path = os.path.join(transchema_data_dir, src_name)
    out_path = os.path.join(cache_dir, f"auto-pipeline-{benchmark}.json")

    if os.path.exists(out_path) and os.path.getmtime(out_path) >= os.path.getmtime(src_path):
        return out_path

    with open(src_path, "r") as f:
        rows = json.load(f)

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["Target Data Name"]].append(row)

    with open(out_path, "w") as f:
        json.dump(grouped, f, indent=2)

    print(f"Wrote grouped JSON for benchmark='{benchmark}' to {out_path}")
    return out_path


def ensure_cases_available(json_file_path, case_pairs, benchmark_dir):
    """For each (length, case_id) not already present in `json_file_path`,
    synthesizes its metadata from that single case's CSVs on disk (cheap: one
    folder at a time, not a scan of the whole benchmark) and appends it to the
    JSON in place. Returns the set of case IDs (e.g. '1_20') that still
    couldn't be resolved (missing on disk too)."""
    with open(json_file_path, "r") as f:
        grouped = json.load(f)

    benchmark_dir = os.path.abspath(benchmark_dir)
    added = 0
    unresolved = set()
    for length, case_id in case_pairs:
        target_data_name = f"Target{length}_{case_id}"
        if target_data_name in grouped:
            continue
        case_dir = os.path.join(benchmark_dir, f"length{length}_{case_id}")
        rows = _synthesize_case_rows(length, case_id, case_dir)
        if rows:
            grouped[target_data_name] = rows
            added += 1
        else:
            unresolved.add(f"{length}_{case_id}")

    if added:
        with open(json_file_path, "w") as f:
            json.dump(grouped, f, indent=2)
        print(f"Synthesized metadata for {added} case(s) directly from disk (not present in the metadata JSON)")

    return unresolved


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare Transchema JSON for SQLMorpher")
    parser.add_argument("--benchmark", choices=list(_BENCHMARK_JSON), default="github")
    parser.add_argument("--transchema-data-dir", default="../data")
    args = parser.parse_args()
    build_grouped_json(args.benchmark, args.transchema_data_dir)
