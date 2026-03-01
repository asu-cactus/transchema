#!/usr/bin/env python3
"""
Clean Milvus DB or drop collections.

Use this script when you need to reset the Milvus database or remove a collection.
Unlike ingest_texts.py (which no longer deletes the DB), this script provides
explicit cleanup options.

Examples:
    # Drop a specific collection (DB file stays)
    python -m rag_pipeline.clean_milvus_db --db-path rag_pipeline/db/milvus_demo_4.db --action drop_collection --collection plan_docs

    # Delete the entire DB file (full reset)
    python -m rag_pipeline.clean_milvus_db --db-path rag_pipeline/db/milvus_demo_4.db --action delete_db
"""
import argparse
import os
from pymilvus import MilvusClient


def main():
    ap = argparse.ArgumentParser(
        description="Clean Milvus DB or drop collections."
    )
    ap.add_argument(
        "--db-path",
        type=str,
        default="rag_pipeline/db/milvus_demo_4.db",
        help="Path to the Milvus Lite SQLite DB file.",
    )
    ap.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["drop_collection", "delete_db"],
        help="Action: drop_collection (remove one collection) or delete_db (delete entire DB file).",
    )
    ap.add_argument(
        "--collection",
        type=str,
        default="plan_docs",
        help="Collection name (required when action=drop_collection).",
    )
    args = ap.parse_args()

    if args.action == "drop_collection":
        milvus = MilvusClient(args.db_path)
        if milvus.has_collection(args.collection):
            milvus.drop_collection(args.collection)
            print(f"[INFO] Dropped collection: {args.collection}")
        else:
            print(f"[INFO] Collection {args.collection} does not exist, nothing to drop.")
        del milvus

    elif args.action == "delete_db":
        if os.path.exists(args.db_path):
            os.remove(args.db_path)
            print(f"[INFO] Deleted DB file: {args.db_path}")
        else:
            print(f"[INFO] DB file does not exist: {args.db_path}")


if __name__ == "__main__":
    main()
