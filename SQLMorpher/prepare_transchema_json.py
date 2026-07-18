"""Converts Transchema's flat Auto-Pipeline JSON (list of source/target rows)
into the grouped-by-target format that `auto_pipeline_join.gpt_auto_pipeline`
expects (dict: Target Data Name -> list of rows), so SQLMorpher can run on the
exact same dataset as Transchema without touching Excel files.
"""

import json
import os
from collections import defaultdict

_BENCHMARK_JSON = {
    "github": "chatgpt_github_ms.json",
    "monteprep": "chatgpt_monteprep_ms.json",
}


def build_grouped_json(benchmark="github", transchema_data_dir="../data", cache_dir="."):
    """Returns the path to a grouped JSON file for `benchmark`, building it
    from Transchema's flat JSON if not already cached."""
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare Transchema JSON for SQLMorpher")
    parser.add_argument("--benchmark", choices=list(_BENCHMARK_JSON), default="github")
    parser.add_argument("--transchema-data-dir", default="../data")
    args = parser.parse_args()
    build_grouped_json(args.benchmark, args.transchema_data_dir)
