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


def _read_schema_and_samples(csv_path, n_samples=3):
    df = pd.read_csv(csv_path, low_memory=False, nrows=200)
    schema = list(df.columns)
    samples = df.head(n_samples).values.tolist()
    return schema, samples


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


def _augment_with_disk_cases(grouped, benchmark_dir):
    """Adds synthesized entries for any length{L}_{id} folder on disk that
    isn't already covered by the metadata JSON."""
    benchmark_dir = os.path.abspath(benchmark_dir)
    if not os.path.isdir(benchmark_dir):
        return grouped, 0

    added = 0
    for entry in sorted(os.listdir(benchmark_dir)):
        match = _CASE_DIR_RE.match(entry)
        if not match:
            continue
        length, case_id = match.groups()
        target_data_name = f"Target{length}_{case_id}"
        if target_data_name in grouped:
            continue
        case_dir = os.path.join(benchmark_dir, entry)
        rows = _synthesize_case_rows(length, case_id, case_dir)
        if rows:
            grouped[target_data_name] = rows
            added += 1

    return grouped, added


def build_grouped_json(benchmark="github", transchema_data_dir="../data", cache_dir=".",
                        benchmark_dir=None, augment_from_disk=True):
    """Returns the path to a grouped JSON file for `benchmark`, building it
    from Transchema's flat JSON (plus, optionally, synthesized entries for any
    on-disk cases missing from that JSON) if not already cached."""
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

    if augment_from_disk:
        benchmark_dir = benchmark_dir or _BENCHMARK_DIRS[benchmark]
        grouped, added = _augment_with_disk_cases(grouped, benchmark_dir)
        if added:
            print(f"Synthesized metadata for {added} case(s) present on disk but missing from {src_path}")

    with open(out_path, "w") as f:
        json.dump(grouped, f, indent=2)

    print(f"Wrote grouped JSON for benchmark='{benchmark}' to {out_path}")
    return out_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare Transchema JSON for SQLMorpher")
    parser.add_argument("--benchmark", choices=list(_BENCHMARK_JSON), default="github")
    parser.add_argument("--transchema-data-dir", default="../data")
    parser.add_argument("--benchmark-dir", default=None)
    parser.add_argument("--no-augment-from-disk", dest="augment_from_disk", action="store_false")
    args = parser.parse_args()
    build_grouped_json(
        args.benchmark, args.transchema_data_dir,
        benchmark_dir=args.benchmark_dir, augment_from_disk=args.augment_from_disk,
    )
