# ingest_texts_rag_layer.py
import os
from pathlib import Path
from tqdm.auto import tqdm
import argparse
from pymilvus import MilvusClient
from rag_pipeline.rag_layer import RAGDB


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

    p.add_argument(
        "--drop-collection", "--overwrite", "--replace",
        action="store_true",
        dest="drop_collection",
        help="Drop the target collection before ingesting (clean start). Prevents duplicates when re-ingesting. Aliases: --overwrite, --replace. Default: append to existing."
    )

    return p.parse_args()


def load_texts(glob_pattern: str):
    """
    Load text files matching the glob pattern, checking multiple locations:
    1. Current working directory (for flexibility)
    2. transchema/rag-examples-w-pipeline/ (relative to transchema/, where code lives)
    3. Workspace root rag-examples-w-pipeline/ (fallback)
    """
    files = []
    
    # Try current directory first
    files = sorted(Path().glob(glob_pattern))
    
    # If no files found, try transchema/ directory
    if not files:
        transchema_dir = Path(__file__).parent.parent  # transchema/rag_pipeline -> transchema
        files = sorted(transchema_dir.glob(glob_pattern))
    
    # If still no files, try workspace root
    if not files:
        workspace_root = Path(__file__).parent.parent.parent  # transchema/rag_pipeline -> transchema -> workspace root
        files = sorted(workspace_root.glob(glob_pattern))
    docs = []
    case_ids = []
    for fp in tqdm(files, desc="Reading files"):
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore").strip()
            if text:
                docs.append(text)
                # Extract case_id from folder name
                # e.g., "rag-examples-w-pipeline/Length4_24/Length4_24.txt"
                #  folder_name = "Length4_24" → case_id = "4_24"
                folder_name = fp.parent.name  # e.g., "Length4_24"
                if folder_name.startswith("Length"):
                    case_id = folder_name.replace("Length", "")  # "4_24"
                    case_ids.append(case_id)
                else:
                    # Fallback: try to extract from filename or use None
                    case_ids.append(None)
        except Exception as e:
            print(f"[skip] {fp}: {e}")
    return docs, case_ids

def main():
    milvus = MilvusClient(DB_PATH)
    collection_exists = milvus.has_collection(COLLECTION)

    # Optionally drop the collection for a clean ingest (DB file is left intact)
    if DROP_COLLECTION:
        if collection_exists:
            print(f"[INFO] Dropping existing collection: {COLLECTION}")
            milvus.drop_collection(COLLECTION)
        else:
            print(f"[INFO] Collection {COLLECTION} does not exist, skipping drop.")
    elif collection_exists:
        print(
            f"[WARNING] Collection {COLLECTION} already exists. Documents will be appended, "
            "which may create duplicates if you re-ingest the same docs. "
            "Use --drop-collection (or --overwrite/--replace) for a clean start."
        )

    del milvus

    db = RAGDB(
        uri=DB_PATH,
        collection=COLLECTION,
        model_id=MODEL_ID,
        device=DEVICE,
        max_len=MAX_SEQ_LEN
    )

    docs, case_ids = load_texts(SRC_GLOB)
    print(f"Loaded {len(docs)} documents from {SRC_GLOB}")
    if case_ids and any(case_ids):
        print(f"Extracted case_ids for {sum(1 for cid in case_ids if cid)} documents")

    # Insert in small batches
    total = 0
    for i in tqdm(range(0, len(docs), BATCH_SIZE), desc="Inserting"):
        batch_docs = docs[i:i + BATCH_SIZE]
        batch_case_ids = case_ids[i:i + BATCH_SIZE] if case_ids else None
        db.insert_texts(batch_docs, case_ids=batch_case_ids)
        total += len(batch_docs)

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
    DROP_COLLECTION = args.drop_collection
    main()
