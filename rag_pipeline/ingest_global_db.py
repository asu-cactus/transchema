"""
ingest_global_db.py — Build the global schema embedding DB from unused_pipeline_cases.jsonl.

Run once before experiments:

    python rag_pipeline/ingest_global_db.py \
        --jsonl unused_pipeline_cases.jsonl \
        --db rag_pipeline/db/global_schema.db

Options
-------
  --jsonl     Path to the JSONL file (default: unused_pipeline_cases.jsonl)
  --db        Output Milvus DB path (default: rag_pipeline/db/global_schema.db)
  --model     Embedding model ID (default: Qwen/Qwen3-Embedding-0.6B)
  --device    auto | cuda | cpu | mps  (default: auto)
  --batch     Embedding batch size (default: 64)
  --force     Re-ingest even if the collection already has data
"""
import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from rag_pipeline.global_rag_db import GlobalSchemaDB


def main():
    parser = argparse.ArgumentParser(description="Build global schema RAG DB")
    parser.add_argument(
        "--jsonl",
        default="unused_pipeline_cases.jsonl",
        help="Path to unused_pipeline_cases.jsonl",
    )
    parser.add_argument(
        "--db",
        default="rag_pipeline/db/global_schema.db",
        help="Output Milvus DB path",
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen3-Embedding-0.6B",
        help="HuggingFace embedding model ID",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cuda", "cpu", "mps"],
        help="Compute device for embedding",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=64,
        help="Embedding batch size",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Re-ingest even if collection already has data",
    )
    args = parser.parse_args()

    os.chdir(_ROOT)
    os.makedirs(os.path.dirname(args.db) or ".", exist_ok=True)

    print(f"[ingest] JSONL : {args.jsonl}")
    print(f"[ingest] DB    : {args.db}")
    print(f"[ingest] Model : {args.model}")
    print(f"[ingest] Device: {args.device}")
    print(f"[ingest] Batch : {args.batch}")

    gdb = GlobalSchemaDB(db_path=args.db, model_id=args.model, device=args.device)
    n = gdb.build_from_jsonl(
        jsonl_path=args.jsonl,
        batch_size=args.batch,
        skip_existing=not args.force,
    )
    total = gdb.count()
    print(f"[ingest] Done. Inserted {n} new records. Total in DB: {total}")


if __name__ == "__main__":
    main()
