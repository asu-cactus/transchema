# RAG Pipeline Documentation

This document describes the architecture and usage of the **`rag_pipeline`** package and its integration with the **`critique`** framework. It covers each module in the pipeline, the command-line interfaces, and how they interact.

---

## 1. Overview

`rag_pipeline` provides a lightweight **Retrieval-Augmented Generation (RAG)** layer that stores text documents as embeddings in a **Milvus Lite** vector database. These stored examples are later used for few-shot prompting within the `critique` system.

### Core Components

* **`rag_layer.py`** — Embedding model and Milvus interface (RAGDB class)
* **`ingest_texts.py`** — CLI tool to ingest `.txt` files into Milvus
* **`milvus_result_utils.py`** — Converts Milvus search results into JSON
* **Integration:** `critique.py` and `critique_data.py` use the RAG layer to retrieve relevant examples dynamically.

### Typical Workflow

1. Ingest documents into the RAG database using `ingest_texts.py`.
2. Test retrieval using `rag_layer.py`.
3. Enable RAG-driven few-shot retrieval in the critique pipeline (`critique_data.py --few_shot`).

---

## 2. Module: `rag_pipeline.rag_layer`

### Purpose

Defines the **`RAGDB`** class and **`EmbeddingLayer`**, responsible for:

* Loading HuggingFace embedding models
* Computing vector embeddings
* Storing and searching documents in Milvus Lite

### Key Classes

#### `EmbeddingLayer`

Handles model loading and encoding.

```python
EmbeddingLayer(
    model_id="Qwen/Qwen3-Embedding-0.6B",
    device="auto"
)
```

* Auto-selects device (`cuda`, `mps`, `cpu`).
* `encode(docs, is_query=False, normalize_embeddings=True, batch_size=1)`

  * Encodes text to embeddings.
  * Supports last-token or pooled outputs.
  * Normalizes embeddings (L2).

#### `RAGDB`

Connects to Milvus Lite and provides APIs for document insertion and search.

```python
RAGDB(
    uri="rag_pipeline/test_dummy/milvus_demo_4.db",
    collection="plan_docs",
    model_id="Qwen/Qwen3-Embedding-0.6B",
    max_len=8192,
    device="auto"
)
```

**Methods:**

* `insert_texts(texts: list[str])` — embeds and stores texts into Milvus.
* `search(queries: list[str], top_k=5, batch_size=32)` — retrieves top-k nearest documents.
* `_embed(texts, bs=32)` — internal helper for batched embedding.

**Demo Mode:**
Running standalone (`python -m rag_pipeline.rag_layer`) executes a sample search (`"debt consolidation"`) and prints formatted results.

---

## 3. Module: `rag_pipeline.milvus_result_utils`

### Purpose

Converts Milvus search results to JSON for use in `critique.py`.

### Key Function

```python
milvus_results_to_json(results, output_fields)
```

**Parameters:**

* `results`: Milvus search response object
* `output_fields`: list of fields to extract (e.g., `["doc"]`)

**Output Example:**

```json
[
  {"id": "123", "distance": 0.12, "doc": "Example text..."},
  {"id": "456", "distance": 0.17, "doc": "Another doc..."}
]
```

---

## 4. Module: `rag_pipeline.ingest_texts`

### Purpose

Populates Milvus with documents for RAG.

### Arguments

| Argument        | Description                          | Default                                    |
| --------------- | ------------------------------------ | ------------------------------------------ |
| `--db-path`     | Path to Milvus Lite DB               | `rag_pipeline/test_dummy/milvus_demo_4.db` |
| `--src-glob`    | Glob pattern for source `.txt` files | `rag_pipeline/source_texts/only*/*.txt`    |
| `--collection`  | Collection name                      | `plan_docs`                                |
| `--model-id`    | Embedding model ID                   | `Qwen/Qwen3-Embedding-0.6B`                |
| `--device`      | Compute device                       | `auto`                                     |
| `--batch-size`  | Batch size for embedding             | `1`                                        |
| `--max-seq-len` | Max token length                     | `8192`                                     |

### Command Example

```bash
python -m rag_pipeline.ingest_texts \
  --db-path rag_pipeline/test_dummy/milvus_demo_4.db \
  --src-glob "rag_pipeline/source_texts/only*/*.txt" \
  --collection plan_docs \
  --model-id Qwen/Qwen3-Embedding-0.6B \
  --device auto \
  --batch-size 4 \
  --max-seq-len 8192
```

**Behavior:**

* Deletes existing DB (fresh start each run)
* Loads text files and strips whitespace
* Embeds and inserts batches into Milvus
* Reports total documents inserted

---

## 5. Integration with `critique.py` and `critique_data.py`

### In `critique.py`

* Imports `RAGDB` and `milvus_results_to_json`.
* Creates `rag_db` when `--few_shot` is enabled:

  ```python
  rag_db = RAGDB(
      uri=args.rag_db_uri,
      model_id=args.rag_embedding_model,
      collection=args.rag_db_collection,
      max_len=args.rag_embedding_dim
  )
  ```
* Performs retrieval:

  ```python
  results = rag_db.search(aux_query, top_k=args.rag_topk)
  rag_json = milvus_results_to_json(results, output_fields=args.rag_output_fields)
  ```
* Injects few-shot examples into the LLM prompt dynamically.

### In `critique_data.py`

Defines all CLI arguments for RAG integration:

* `--rag_db_uri`, `--rag_embedding_model`, `--rag_db_collection`
* `--rag_embedding_dim`, `--rag_embedding_batch_size`
* `--rag_topk`, `--rag_output_fields`
* `--few_shot` flag to enable RAG-driven example retrieval.

### Example Command (Full Critique Pipeline)

```bash
python critique_data.py \
  --few_shot \
  --rag_db_uri rag_pipeline/test_dummy/milvus_demo_4.db \
  --rag_db_collection plan_docs \
  --rag_embedding_model Qwen/Qwen3-Embedding-0.6B \
  --rag_embedding_dim 8192 \
  --rag_topk 3 \
  --rag_embedding_batch_size 2 \
  --rag_output_fields doc
```

This command:

* Loads Milvus DB
* Retrieves top-k similar examples for each query
* Injects them as few-shot prompts into LLM critiques

---

## 6. Summary

> The `rag_pipeline` framework integrates **vector-based retrieval** into the critique system. It uses **Milvus Lite** as the backend and a **HuggingFace embedding model** to encode text documents. Through the `RAGDB` interface, the critique modules can dynamically retrieve semantically similar examples, enabling context-aware few-shot reasoning and more accurate code critiques.
