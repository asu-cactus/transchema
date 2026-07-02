"""
Build a numpy-backed GlobalFeatureDB from unused_pipeline_cases_enriched.jsonl.

Usage
-----
  python rag_pipeline/ingest_global_feature_db.py \\
      --jsonl unused_pipeline_cases_enriched.jsonl \\
      --db rag_pipeline/db/global_features

Pass --force to rebuild an existing index.
"""
from __future__ import annotations

import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build GlobalFeatureDB from enriched JSONL."
    )
    p.add_argument(
        "--jsonl",
        required=True,
        help="Path to unused_pipeline_cases_enriched.jsonl",
    )
    p.add_argument(
        "--db",
        required=True,
        help="Output db path prefix (e.g. rag_pipeline/db/global_features)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Rebuild even if the index already exists.",
    )
    args = p.parse_args()

    from rag_pipeline.global_rag_db import GlobalFeatureDB

    db = GlobalFeatureDB(db_path=args.db)
    n = db.build_from_jsonl(args.jsonl, skip_existing=not args.force)
    if n > 0:
        print(f"[done] Indexed {n} records at {args.db}")
    else:
        print("[done] Index already existed — use --force to rebuild.")


if __name__ == "__main__":
    main()
