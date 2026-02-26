"""
Ingest feature vectors into a Milvus collection for feature-based RAG retrieval.

Reads each case folder under rag-examples-w-pipeline (Source_datasets, Target_datasets,
operator_pipeline.txt), computes a 23-dim vector, and inserts (vector, case_id) into
the feature collection. Run this after or alongside text ingest.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from pymilvus import MilvusClient
from tqdm.auto import tqdm

from .feature_extractor import FEATURE_DIM, compute_from_case_folder


def _resolve_rag_examples_base(base: str) -> Path:
    p = Path(base)
    if p.is_absolute() and p.exists():
        return p
    # Try cwd
    cwd = Path.cwd()
    if (cwd / base).exists():
        return (cwd / base).resolve()
    # Try next to this file: transchema/rag_pipeline -> transchema
    transchema = Path(__file__).resolve().parent.parent
    if (transchema / base).exists():
        return (transchema / base).resolve()
    # Try workspace root (transchema parent)
    root = transchema.parent
    if (root / base).exists():
        return (root / base).resolve()
    return Path(base).resolve()


def get_args():
    p = argparse.ArgumentParser(
        description="Ingest 23-dim feature vectors into Milvus for feature-based RAG."
    )
    p.add_argument(
        "--rag-examples-base",
        type=str,
        default="rag-examples-w-pipeline",
        help="Path to rag-examples-w-pipeline (or folder containing Length* case dirs).",
    )
    p.add_argument(
        "--db-path",
        type=str,
        default="rag_pipeline/db/milvus_demo_4.db",
        help="Path to Milvus Lite SQLite DB (same as text RAG or separate).",
    )
    p.add_argument(
        "--collection",
        type=str,
        default="plan_docs_features",
        help="Milvus collection name for feature vectors.",
    )
    p.add_argument(
        "--drop-collection",
        action="store_true",
        dest="drop_collection",
        help="Drop the feature collection before ingesting (clean start).",
    )
    return p.parse_args()


def main():
    args = get_args()
    base = _resolve_rag_examples_base(args.rag_examples_base)
    if not base.exists():
        raise FileNotFoundError(f"rag-examples base not found: {base}")

    case_folders = sorted(base.glob("Length*"))
    if not case_folders:
        raise FileNotFoundError(f"No Length* folders under {base}")

    client = MilvusClient(args.db_path)
    if args.drop_collection and client.has_collection(args.collection):
        print(f"[INFO] Dropping existing collection: {args.collection}")
        client.drop_collection(args.collection)

    if not client.has_collection(args.collection):
        client.create_collection(
            collection_name=args.collection,
            dimension=FEATURE_DIM,
            metric_type="COSINE",
            auto_id=True,
            enable_dynamic_field=True,
        )
    try:
        client.load_collection(args.collection)
    except Exception:
        pass

    case_ids = []
    vectors = []
    skipped = 0
    for case_folder in tqdm(case_folders, desc="Computing features"):
        try:
            vec, case_id = compute_from_case_folder(case_folder)
            if len(vec) != FEATURE_DIM:
                skipped += 1
                continue
            if case_id is None:
                skipped += 1
                continue
            vectors.append(vec)
            case_ids.append(case_id)
        except Exception as e:
            tqdm.write(f"[skip] {case_folder.name}: {e}")
            skipped += 1

    if not vectors:
        print("[WARN] No vectors to insert.")
        return

    rows = [
        {"vector": vectors[i], "case_id": case_ids[i]}
        for i in range(len(vectors))
    ]
    client.insert(collection_name=args.collection, data=rows)
    print(f"Inserted {len(rows)} feature vectors into {args.collection} (skipped {skipped})")


if __name__ == "__main__":
    main()
