"""
global_rag_db.py — Global schema-embedding database for two-tier RAG.

Architecture
------------
  Tier 1 (this file): numpy-based vector store keyed on concatenated
  target+source schema column names.  Built once offline from
  unused_pipeline_cases.jsonl.  At runtime, embed the current case's
  schemas and retrieve the top-50 most similar examples via cosine similarity.

  No file locking — multiple parallel MCTS processes can search simultaneously
  because the numpy array is opened read-only and never written at search time.

  Tier 2: local_rag_db.py — per-case SQLite populated from those 50 results,
  queried via operator-prefix match during MCTS expansion (unchanged).

Storage (written once by ingest_global_db.py)
----------------------------------------------
  <db_path>.embeddings.npy   float32 array (N, dim) — one row per example
  <db_path>.records.json     list of N metadata dicts
  <db_path>.meta.json        {"model_id": "..."}

Usage
-----
  # Build (offline, once):
  python rag_pipeline/ingest_global_db.py \
      --jsonl unused_pipeline_cases.jsonl \
      --db rag_pipeline/db/global_schema

  # Query (at runtime, inside mcts_search.py):
  from rag_pipeline.global_rag_db import GlobalSchemaDB
  gdb = GlobalSchemaDB("rag_pipeline/db/global_schema")
  results = gdb.search(target_schema="col1, col2", source_schemas=["colA, colB"], top_k=50)
  # results: List[dict] ready for local_rag_db.populate_from_global_results()
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

import numpy as np

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

# Workaround: torchvision may be installed at an incompatible version with torch
# (e.g. torchvision 0.21 against torch 2.4.x), causing _meta_registrations to
# crash when transformers' image_utils.py tries to import it.  We patch
# importlib.util.find_spec to report torchvision as absent so that
# transformers skips the optional import entirely.
import importlib.util as _ilu

_orig_find_spec = _ilu.find_spec


def _find_spec_no_tv(name, *args, **kwargs):
    if name == "torchvision" or (name or "").startswith("torchvision."):
        return None
    return _orig_find_spec(name, *args, **kwargs)


_ilu.find_spec = _find_spec_no_tv

_DEFAULT_MODEL = "Qwen/Qwen3-Embedding-0.6B"
_MAX_SEQ_LEN = 512


# ── Low-level embedding ───────────────────────────────────────────────────────


def _last_token_pool(last_hidden_states, attention_mask, device):
    import torch
    left_padding = attention_mask[:, -1].sum() == attention_mask.shape[0]
    if left_padding:
        return last_hidden_states[:, -1]
    seq_lengths = attention_mask.sum(dim=1) - 1
    batch_size = last_hidden_states.shape[0]
    return last_hidden_states[torch.arange(batch_size, device=device), seq_lengths]


class _EmbeddingLayer:
    def __init__(self, model_id: str = _DEFAULT_MODEL, device: str = "auto"):
        import torch
        from transformers import AutoTokenizer, AutoModel

        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        self.device = device
        self._torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, padding_side="left", trust_remote_code=True
        )
        self.model = (
            AutoModel.from_pretrained(model_id, trust_remote_code=True)
            .to(self.device)
            .eval()
        )

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        from tqdm.auto import tqdm
        import torch.nn.functional as F

        torch = self._torch
        chunks = []
        with torch.inference_mode():
            for start in tqdm(range(0, len(texts), batch_size), desc="Embedding"):
                batch = texts[start : start + batch_size]
                enc = self.tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    max_length=_MAX_SEQ_LEN,
                    return_tensors="pt",
                )
                enc = {k: v.to(self.device) for k, v in enc.items()}
                out = self.model(**enc)
                if getattr(out, "pooler_output", None) is not None:
                    pooled = out.pooler_output
                else:
                    pooled = _last_token_pool(
                        out.last_hidden_state, enc["attention_mask"], self.device
                    )
                pooled = F.normalize(pooled, p=2, dim=-1)
                chunks.append(pooled.detach().cpu().to(torch.float32).numpy())
        return np.concatenate(chunks, axis=0).astype("float32")


# ── Schema text helpers ───────────────────────────────────────────────────────


def format_schema_text(
    target_schema: "str | list",
    source_schemas: "list",
) -> str:
    """Format target + source schemas into a single embedding string.

    Output: "target: col1, col2 | source_0: colA, colB | source_1: colX"
    """
    def _to_str(s) -> str:
        return ", ".join(str(c) for c in s) if isinstance(s, list) else str(s)

    parts = [f"target: {_to_str(target_schema)}"]
    for i, src in enumerate(source_schemas):
        parts.append(f"source_{i}: {_to_str(src)}")
    return " | ".join(parts)


# ── Global DB class ───────────────────────────────────────────────────────────


class GlobalSchemaDB:
    """Numpy-backed global schema embedding store.

    At build time: embeddings saved to <db_path>.embeddings.npy,
                   metadata saved to <db_path>.records.json,
                   model id saved to <db_path>.meta.json.

    At search time: files are loaded read-only into memory — no file lock,
                    safe for any number of concurrent processes.
    """

    def __init__(
        self,
        db_path: str,
        model_id: Optional[str] = None,
        device: str = "auto",
    ):
        # Strip legacy .db suffix so both "global_schema" and
        # "global_schema.db" resolve to the same files.
        self.db_path = db_path.removesuffix(".db") if db_path.endswith(".db") else db_path
        self._emb_path = self.db_path + ".embeddings.npy"
        self._rec_path = self.db_path + ".records.json"
        self._meta_path = self.db_path + ".meta.json"

        self._device = device
        self._embedder: Optional[_EmbeddingLayer] = None

        # Auto-read model_id from meta file if not explicitly given
        self._model_id = model_id or self._read_meta().get("model_id", _DEFAULT_MODEL)

        # Load embeddings + records into memory (read-only)
        self._embeddings: Optional[np.ndarray] = None
        self._records: Optional[List[Dict]] = None
        self._load_index()

    # ── sidecar helpers ──────────────────────────────────────────────────────

    def _read_meta(self) -> dict:
        if os.path.exists(self._meta_path):
            try:
                with open(self._meta_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _write_meta(self) -> None:
        with open(self._meta_path, "w") as f:
            json.dump({"model_id": self._model_id}, f)

    def _load_index(self) -> None:
        if os.path.exists(self._emb_path) and os.path.exists(self._rec_path):
            self._embeddings = np.load(self._emb_path)
            with open(self._rec_path) as f:
                self._records = json.load(f)

    # ── lazy embedder ────────────────────────────────────────────────────────

    def _get_embedder(self) -> _EmbeddingLayer:
        if self._embedder is None:
            print(f"[GlobalSchemaDB] Loading embedding model: {self._model_id}")
            self._embedder = _EmbeddingLayer(model_id=self._model_id, device=self._device)
        return self._embedder

    # ── ingestion ────────────────────────────────────────────────────────────

    def build_from_jsonl(
        self,
        jsonl_path: str,
        batch_size: int = 256,
        skip_existing: bool = True,
    ) -> int:
        """Embed all examples and save to .embeddings.npy + .records.json.

        Args:
            jsonl_path:    Path to unused_pipeline_cases.jsonl.
            batch_size:    Embedding batch size.
            skip_existing: Skip if output files already exist.

        Returns:
            Number of records embedded.
        """
        if skip_existing and os.path.exists(self._emb_path) and os.path.exists(self._rec_path):
            existing = np.load(self._emb_path).shape[0]
            print(f"[GlobalSchemaDB] Index already exists ({existing} records) — skipping.")
            self._write_meta()
            return 0

        records = []
        with open(jsonl_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        print(f"[GlobalSchemaDB] Loaded {len(records)} records from {jsonl_path}")

        schema_texts = []
        metas = []
        for rec in records:
            tgt_schema = rec.get("target", {}).get("schema", [])
            src_schemas = [v.get("schema", []) for v in rec.get("inputs", {}).values()]
            schema_texts.append(format_schema_text(tgt_schema, src_schemas))
            metas.append(_extract_metadata(rec))

        embedder = self._get_embedder()
        embeddings = embedder.encode(schema_texts, batch_size=batch_size)

        np.save(self._emb_path, embeddings)
        with open(self._rec_path, "w") as f:
            json.dump(metas, f)
        self._write_meta()

        print(f"[GlobalSchemaDB] Saved {len(metas)} records → {self._emb_path}")
        self._load_index()
        return len(metas)

    # ── search ───────────────────────────────────────────────────────────────

    def search(
        self,
        target_schema: "str | list",
        source_schemas: "list",
        top_k: int = 50,
    ) -> List[Dict]:
        """Return top_k most similar examples via cosine similarity.

        Safe to call from multiple parallel processes — read-only numpy ops.
        """
        if self._embeddings is None or self._records is None:
            raise RuntimeError(
                f"[GlobalSchemaDB] Index not found at {self.db_path}. "
                "Run ingest_global_db.py first."
            )

        query_text = format_schema_text(target_schema, source_schemas)
        embedder = self._get_embedder()
        qvec = embedder.encode([query_text], batch_size=1)  # (1, dim)

        # Cosine similarity: embeddings are L2-normalised, so dot product = cosine
        sims = (self._embeddings @ qvec.T).squeeze()  # (N,)
        top_idx = np.argpartition(sims, -top_k)[-top_k:]
        top_idx = top_idx[np.argsort(sims[top_idx])[::-1]]

        results = []
        for idx in top_idx:
            meta = dict(self._records[int(idx)])
            meta["sim_score"] = float(sims[idx])
            results.append(meta)
        return results

    def count(self) -> int:
        return len(self._records) if self._records is not None else 0


# ── Metadata extraction from a JSONL record ──────────────────────────────────


def _extract_metadata(rec: dict) -> dict:
    tgt = rec.get("target", {})
    tgt_schema = tgt.get("schema", [])
    tgt_samples = tgt.get("sample", [])

    inputs = rec.get("inputs", {})
    src_schemas: Dict[str, str] = {}
    src_samples: Dict[str, str] = {}
    for tbl, v in inputs.items():
        cols = v.get("schema", [])
        rows = v.get("sample", [])
        src_schemas[tbl] = ", ".join(str(c) for c in cols)
        src_samples[tbl] = _samples_to_text(cols, rows)

    return {
        "case_id": rec.get("case", "unknown"),
        "pipeline": rec.get("pipeline", ""),
        "operators": rec.get("operators", []),
        "target_schema": ", ".join(str(c) for c in tgt_schema),
        "target_samples": _samples_to_text(tgt_schema, tgt_samples),
        "source_schemas": src_schemas,
        "source_samples": src_samples,
    }


def _samples_to_text(cols: list, rows: list, max_rows: int = 3) -> str:
    if not cols or not rows:
        return ""
    lines = ["\t".join(str(c) for c in cols)]
    for row in rows[:max_rows]:
        lines.append("\t".join(str(v) for v in row))
    return "\n".join(lines)


# ── Global feature-vector DB ──────────────────────────────────────────────────


class GlobalFeatureDB:
    """Numpy-backed global store for 22-dim z-score normalised feature vectors.

    Same on-disk layout as GlobalSchemaDB (.embeddings.npy, .records.json,
    .meta.json) so the retrieval path in mcts_search is identical — just swap
    the class.  No embedding model: vectors are computed analytically from the
    enriched JSONL via compute_from_jsonl_record().

    Concurrent reads are safe (numpy read-only); writes happen only at build time.

    Storage (written once by ingest_global_feature_db.py)
    -------------------------------------------------------
      <db_path>.embeddings.npy   float32 (N, 22) — z-score + L2-normalised
      <db_path>.records.json     list of N metadata dicts (same schema as GlobalSchemaDB)
      <db_path>.meta.json        {"norm_stats": {"mean": [...], "std": [...]}}

    Usage
    -----
      # Build (offline, once):
      python rag_pipeline/ingest_global_feature_db.py \\
          --jsonl unused_pipeline_cases_enriched.jsonl \\
          --db rag_pipeline/db/global_features

      # Query (at runtime, inside mcts_search.py):
      from rag_pipeline.global_rag_db import GlobalFeatureDB
      fdb = GlobalFeatureDB("rag_pipeline/db/global_features")
      results = fdb.search(source_dfs, target_df, top_k=50)
      # results: List[dict] ready for local_rag_db.populate_from_global_results()
    """

    def __init__(self, db_path: str):
        self.db_path = db_path.removesuffix(".db") if db_path.endswith(".db") else db_path
        self._emb_path = self.db_path + ".embeddings.npy"
        self._rec_path = self.db_path + ".records.json"
        self._meta_path = self.db_path + ".meta.json"

        self._embeddings: Optional[np.ndarray] = None
        self._records: Optional[List[Dict]] = None
        self._norm_stats: Optional[Dict] = None
        self._load_index()

    # ── sidecar helpers ──────────────────────────────────────────────────────

    def _read_meta(self) -> dict:
        if os.path.exists(self._meta_path):
            try:
                with open(self._meta_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _write_meta(self, norm_stats: dict) -> None:
        with open(self._meta_path, "w") as f:
            json.dump({"norm_stats": norm_stats}, f)

    def _load_index(self) -> None:
        if os.path.exists(self._emb_path) and os.path.exists(self._rec_path):
            self._embeddings = np.load(self._emb_path)
            with open(self._rec_path) as f:
                self._records = json.load(f)
            self._norm_stats = self._read_meta().get("norm_stats")

    # ── ingestion ────────────────────────────────────────────────────────────

    def build_from_jsonl(
        self,
        jsonl_path: str,
        skip_existing: bool = True,
    ) -> int:
        """Compute feature vectors for all records and save to disk.

        Args:
            jsonl_path:    Path to unused_pipeline_cases_enriched.jsonl.
            skip_existing: Skip if output files already exist.

        Returns:
            Number of records indexed (0 if skipped).
        """
        from rag_pipeline.feature_extractor import (
            compute_from_jsonl_record,
            compute_norm_stats,
            zscore_normalize,
        )

        if skip_existing and os.path.exists(self._emb_path) and os.path.exists(self._rec_path):
            existing = np.load(self._emb_path).shape[0]
            print(f"[GlobalFeatureDB] Index already exists ({existing} records) — skipping.")
            return 0

        records = []
        with open(jsonl_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        print(f"[GlobalFeatureDB] Loaded {len(records)} records from {jsonl_path}")

        raw_vectors = []
        metas = []
        skipped = 0
        for rec in records:
            try:
                raw_vectors.append(compute_from_jsonl_record(rec))
                metas.append(_extract_metadata(rec))
            except Exception:
                skipped += 1

        if not raw_vectors:
            print("[GlobalFeatureDB] No vectors computed — aborting.")
            return 0

        # Zero out op_hist dims before normalisation.
        # At query time the operator histogram is always zero (no operators known
        # yet), so keeping real op_hist values in stored vectors creates a
        # systematic bias: the query aligns with "no-op / terminal" cases rather
        # than structurally similar ones.  Zeroing here makes both sides
        # consistent; structural features (n_inputs, cols, rows, overlap, …)
        # drive retrieval instead.
        from rag_pipeline.feature_extractor import OP_HIST_SLICE
        for v in raw_vectors:
            for i in range(*OP_HIST_SLICE.indices(len(v))):
                v[i] = 0.0

        # Z-score normalise across the corpus, then L2-normalise each vector so
        # dot product == cosine similarity (mirrors GlobalSchemaDB behaviour).
        stats = compute_norm_stats(raw_vectors)
        normalised = np.array(
            [zscore_normalize(v, stats) for v in raw_vectors], dtype="float32"
        )
        norms = np.linalg.norm(normalised, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        normalised = normalised / norms

        np.save(self._emb_path, normalised)
        with open(self._rec_path, "w") as f:
            json.dump(metas, f)
        self._write_meta(stats)

        print(
            f"[GlobalFeatureDB] Saved {len(metas)} records → {self._emb_path}"
            + (f" (skipped {skipped})" if skipped else "")
        )
        self._load_index()
        return len(metas)

    # ── search ───────────────────────────────────────────────────────────────

    def search(
        self,
        source_dfs: list,
        target_df,
        top_k: int = 50,
        exclude_case_id: Optional[str] = None,
    ) -> List[Dict]:
        """Return top_k most similar examples via cosine similarity on feature vectors.

        Safe to call from multiple parallel processes — read-only numpy ops.

        Args:
            source_dfs:       List of source pandas DataFrames for the current task.
            target_df:        Target pandas DataFrame for the current task.
            top_k:            Number of results to return.
            exclude_case_id:  If given, suppress any result whose case_id matches
                              (prevents self-retrieval in upper-bound evaluations).
        """
        from rag_pipeline.feature_extractor import compute_from_data, zscore_normalize

        if self._embeddings is None or self._records is None:
            raise RuntimeError(
                f"[GlobalFeatureDB] Index not found at {self.db_path}. "
                "Run ingest_global_feature_db.py first."
            )
        if self._norm_stats is None:
            raise RuntimeError(
                "[GlobalFeatureDB] Norm stats missing from meta.json. "
                "Rebuild the index with ingest_global_feature_db.py."
            )

        from rag_pipeline.feature_extractor import OP_HIST_SLICE
        raw_vec = compute_from_data(source_dfs, target_df)
        # Zero op_hist — consistent with how stored vectors were built
        for i in range(*OP_HIST_SLICE.indices(len(raw_vec))):
            raw_vec[i] = 0.0
        normalised = zscore_normalize(raw_vec, self._norm_stats)

        qvec = np.array(normalised, dtype="float32")
        qnorm = float(np.linalg.norm(qvec))
        if qnorm > 0:
            qvec = qvec / qnorm

        sims = (self._embeddings @ qvec).squeeze()  # (N,)

        if exclude_case_id is not None:
            for i, meta in enumerate(self._records):
                if meta.get("case_id") == exclude_case_id:
                    sims[i] = -2.0  # below any valid cosine score

        top_idx = np.argpartition(sims, -top_k)[-top_k:]
        top_idx = top_idx[np.argsort(sims[top_idx])[::-1]]

        results = []
        for idx in top_idx:
            meta = dict(self._records[int(idx)])
            meta["sim_score"] = float(sims[idx])
            results.append(meta)
        return results

    def count(self) -> int:
        return len(self._records) if self._records is not None else 0
