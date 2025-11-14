# ingest_texts_rag_layer.py
import os
from pathlib import Path
from tqdm.auto import tqdm
import argparse
from rag_pipeline.rag_layer import RAGDB

# DB_PATH = "rag_pipeline/test_dummy/milvus_demo_4.db"
# # SRC_GLOB = "rag_pipeline/source_texts/**/*.txt"
# SRC_GLOB = "rag_pipeline/source_texts/only*/*.txt"
# COLLECTION = "plan_docs"
# MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
# DEVICE = "auto"
# BATCH_SIZE = 1


def get_args():
    p = argparse.ArgumentParser(
        description="Ingest text files into a Milvus-backed RAG DB."
    )

    p.add_argument(
        "--db-path",
        type=str,
        default="rag_pipeline/test_dummy/milvus_demo_4.db",
        help="Path to the Milvus Lite SQLite DB file."
    )

    p.add_argument(
        "--src-glob",
        type=str,
        default="rag_pipeline/source_texts/only*/*.txt",
        help="Glob pattern for source text files to ingest."
    )

    p.add_argument(
        "--collection",
        type=str,
        default="plan_docs",
        help="Milvus collection name to use/create."
    )

    p.add_argument(
        "--model-id",
        type=str,
        default="Qwen/Qwen3-Embedding-0.6B",
        help="Embedding model ID to use (Hugging Face / sentence-transformers name)."
    )

    p.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cpu", "cuda", "mps"],
        help="Device to run the embedding model on."
    )

    p.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size for embedding documents."
    )

    p.add_argument(
        "--max-seq-len",
        type=int,
        default=8192,
        help="Max sequence length for embedding documents."
    )

    return p.parse_args()


def load_texts(glob_pattern: str):
    files = sorted(Path().glob(glob_pattern))
    docs = []
    for fp in tqdm(files, desc="Reading files"):
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore").strip()
            if text:
                docs.append(text)
        except Exception as e:
            print(f"[skip] {fp}: {e}")
    return docs

def main():
    # Optional: start fresh each run
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass

    db = RAGDB(
        uri=DB_PATH,
        collection=COLLECTION,
        model_id=MODEL_ID,
        device=DEVICE,
        max_len=MAX_SEQ_LEN
    )

    docs = load_texts(SRC_GLOB)
    print(f"Loaded {len(docs)} documents from {SRC_GLOB}")

    # Insert in small batches
    total = 0
    for i in tqdm(range(0, len(docs), BATCH_SIZE), desc="Inserting"):
        batch = docs[i:i + BATCH_SIZE]
        db.insert_texts(batch)
        total += len(batch)

    print(f"Inserted {total} documents into {DB_PATH} (collection: {COLLECTION})")

if __name__ == "__main__":
    args = get_args()

    DB_PATH = args.db_path
    SRC_GLOB = args.src_glob
    COLLECTION = args.collection
    MODEL_ID = args.model_id
    DEVICE = args.device
    BATCH_SIZE = args.batch_size
    MAX_SEQ_LEN = args.max_seq_len
    main()
