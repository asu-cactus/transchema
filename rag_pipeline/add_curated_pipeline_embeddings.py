"""
add_curated_pipeline_embeddings.py — one-time migration: backfill embedding_vector
into the existing curated_pipeline_656.db (built by build_curated_pipeline_db.py),
enabling the "embedding_only" / "prefix_embedding" retrieval modes.

No re-embedding needed: every one of the 656 curated-pipeline case_ids already has a
precomputed text embedding in rag_pipeline/db/global_schema.embeddings.npy (all-MiniLM-L6-v2,
384-dim, L2-normalized) — build_curated_pipeline_db.py already required each case_id to be
present in global_schema.records.json (the same corpus) to build the DB in the first place.
This script just looks each one up by case_id and copies the vector over.

Usage:
    python3 rag_pipeline/add_curated_pipeline_embeddings.py

Run from: ~/transchema/
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import numpy as np

from rag_pipeline.local_rag_db import create_local_rag_db

REPO = _ROOT
DB_PATH = os.path.join(REPO, "rag_pipeline/db/curated_pipeline_656.db")
GLOBAL_RECORDS = os.path.join(REPO, "rag_pipeline/db/global_schema.records.json")
GLOBAL_EMBEDDINGS = os.path.join(REPO, "rag_pipeline/db/global_schema.embeddings.npy")


def main():
    import sqlite3

    if not os.path.exists(DB_PATH):
        print(f"ERROR: {DB_PATH} not found — run build_curated_pipeline_db.py first.")
        sys.exit(1)

    with open(GLOBAL_RECORDS) as f:
        records = json.load(f)
    embeddings = np.load(GLOBAL_EMBEDDINGS)
    print(f"Loaded {len(records)} global-schema records + embeddings {embeddings.shape}")

    case_id_to_vec = {rec["case_id"]: embeddings[i] for i, rec in enumerate(records)}

    # Ensure the column exists (create_local_rag_db is idempotent -- adds it via
    # ALTER TABLE if this DB predates the embedding_vector column).
    create_local_rag_db(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT id, case_id FROM local_context").fetchall()
    print(f"{len(rows)} rows in {DB_PATH}")

    updated, missing = 0, 0
    for row_id, case_id in rows:
        vec = case_id_to_vec.get(case_id)
        if vec is None:
            missing += 1
            continue
        conn.execute(
            "UPDATE local_context SET embedding_vector = ? WHERE id = ?",
            (json.dumps(vec.tolist()), row_id),
        )
        updated += 1
    conn.commit()
    conn.close()

    print(f"Updated {updated} rows with embedding_vector; {missing} case_ids had no match "
          f"in global_schema.records.json (unexpected -- investigate if > 0).")


if __name__ == "__main__":
    main()
