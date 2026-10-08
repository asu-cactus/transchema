"""Curated-pipeline RAG for the critique_data.py experiments (CoT / Chain-of-Operators).

Wraps the same retrieval mcts_search.py uses -- prefix-match the current operation plan
against the static 656-pipeline corpus, then re-rank the matches by cosine similarity on
an 8-dim structural feature vector -- so the CoT and CoO arms can be compared against the
MCTS arm on equal footing.

The two arms differ only in what operation history is passed to the same function:

  * CoT (pipeline-driven) -- one shot, no plan yet, so the prefix is empty. An empty
    prefix matches every corpus pipeline, and the cosine re-rank then picks the top-k
    structurally most similar cases. That is exactly "the k most similar examples".
  * CoO (operator-driven) -- called again before every operator step with the plan built
    so far, mirroring _simulate_operator_level in Langraph/nodes.py.

Neither rag_pipeline/local_rag_db.py nor rag_pipeline/feature_extractor.py is modified
(both are reachable from mcts_search.py); this module only calls them.

The one thing it deliberately does NOT reuse is feature_extractor's
load_source_target_from_folder(), which globs `test_*.csv` unconditionally. Under
--data_split training that would build the query vector from test data while the model
only ever sees training data, so the loading is done here, split-aware.
"""

import json
import os
from pathlib import Path

import pandas as pd

from rag_pipeline.local_rag_db import get_rag_hints

DEFAULT_CURATED_DB = "rag_pipeline/db/curated_pipeline_656.db"
DEFAULT_CURATED_NORM_STATS = "rag_pipeline/db/curated_pipeline_features.norm_stats.json"

# Corpus rows carry their own source/target sample text, and a few are enormous -- one
# match at depth 2 on case 3_2 alone renders 143k tokens, which overflows the prompt and
# makes get_prompt raise "Prompt length ... exceeds maximum tokens". MCTS survives that
# because its get_prompt call sits in a try//except; multi_step's does not, and losing a
# whole case to one oversized corpus row is not a good trade. So the block is capped:
# examples are dropped from the least similar end until it fits.
DEFAULT_RAG_MAX_TOKENS = 8000


def _count_tokens(text):
    """Token length of `text`, falling back to a ~4-chars-per-token estimate if tiktoken
    is unavailable. Only used to decide how many examples fit, so an estimate is fine."""
    try:
        import tiktoken
        return len(tiktoken.get_encoding("o200k_base").encode(text))
    except Exception:
        return len(text) // 4

# Query vectors are constant per (case, split); computing one reads every source table.
_QUERY_VECTOR_CACHE = {}


def _load_split_source_target(folder, data_split):
    """Source frames for `data_split` plus the target frame.

    Mirrors feature_extractor.load_source_target_from_folder (same row cap, same
    Unnamed-column drop) but globs the requested split instead of always `test_*.csv`.
    """
    folder = Path(folder)
    source_dfs = []
    for path in sorted(folder.glob(f"{data_split}_*.csv")):
        try:
            df = pd.read_csv(path, low_memory=False, nrows=100_000)
            source_dfs.append(df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)])
        except Exception:
            continue

    target_df = None
    target_path = folder / "target.csv"
    if target_path.exists():
        try:
            target_df = pd.read_csv(target_path, low_memory=False, nrows=100_000)
            target_df = target_df.loc[
                :, ~target_df.columns.str.contains("^Unnamed", na=False)
            ]
        except Exception:
            pass
    return source_dfs, target_df


def build_query_vector(directory, len_idx_target_idx, norm_stats_path,
                       data_split="test", logger=None):
    """Normalized 8-dim structural feature vector for one case, or None on failure.

    Same construction as mcts_search.py: raw features -> z-score against the corpus norm
    stats -> unit length, so the query lands in the same space as the stored vectors.
    """
    cache_key = (directory, len_idx_target_idx, data_split, norm_stats_path)
    if cache_key in _QUERY_VECTOR_CACHE:
        return _QUERY_VECTOR_CACHE[cache_key]

    vector = None
    try:
        from rag_pipeline.feature_extractor import (
            compute_pipeline_query_features,
            load_norm_stats,
            zscore_normalize,
        )

        folder = Path(directory) / f"length{len_idx_target_idx}"
        source_dfs, target_df = _load_split_source_target(folder, data_split)
        if not source_dfs:
            raise RuntimeError(f"no {data_split}_*.csv source tables in {folder}")

        raw = compute_pipeline_query_features(source_dfs, target_df)
        normed = zscore_normalize(raw, load_norm_stats(norm_stats_path))
        norm = sum(x * x for x in normed) ** 0.5
        vector = [x / norm for x in normed] if norm > 0 else normed

        if logger is not None:
            logger.info(
                f"[curated RAG] query vector computed for case {len_idx_target_idx} "
                f"from {len(source_dfs)} {data_split} source table(s)"
            )
    except Exception as exc:
        if logger is not None:
            logger.warning(f"[curated RAG] query vector failed, RAG disabled: {exc}")

    _QUERY_VECTOR_CACHE[cache_key] = vector
    return vector


class CuratedRag:
    """Per-case retrieval handle. `enabled` is False when the corpus or the query vector
    is unavailable, in which case hints_for() returns "" and the run proceeds without RAG.
    """

    def __init__(self, db_path, query_vector, top_k=3, max_tokens=DEFAULT_RAG_MAX_TOKENS,
                 logger=None):
        self.db_path = db_path
        self.query_vector = query_vector
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.logger = logger

    @property
    def enabled(self):
        return bool(self.db_path) and os.path.exists(self.db_path) and self.query_vector is not None

    def hints_for(self, operation_history=()):
        """Retrieved hint block for the plan so far ([] for the one-shot CoT prompt).

        NO_MORE_OPERATION is stripped first, exactly as Langraph/nodes.py does: it is not
        a structural step, and leaving it in makes the prefix as long as the whole corpus
        pipeline so the "has a next step" guard never fires.
        """
        if not self.enabled:
            return ""
        history = [op for op in operation_history if op != "NO_MORE_OPERATION"]

        # Retrieval is ranked best-first, so asking for fewer examples drops the least
        # similar ones. Shrink until the block fits the budget rather than letting an
        # oversized corpus row blow up the whole prompt.
        for k in range(self.top_k, 0, -1):
            try:
                hints = get_rag_hints(
                    self.db_path, history, top_k=k, query_vector=self.query_vector
                )
            except Exception as exc:
                if self.logger is not None:
                    self.logger.warning(f"[curated RAG] retrieval failed at depth "
                                        f"{len(history)}: {exc}")
                return ""
            if not hints:
                return ""

            n_tokens = _count_tokens(hints)
            if n_tokens <= self.max_tokens:
                if self.logger is not None:
                    dropped = "" if k == self.top_k else f" ({self.top_k - k} dropped to fit)"
                    self.logger.info(
                        f"[curated RAG] top-{k} examples retrieved, {n_tokens} tokens "
                        f"(prefix depth={len(history)}){dropped}"
                    )
                return hints

            if self.logger is not None:
                self.logger.warning(
                    f"[curated RAG] top-{k} block is {n_tokens} tokens > "
                    f"{self.max_tokens} budget at depth {len(history)} — retrying with "
                    f"{k - 1}"
                )

        if self.logger is not None:
            self.logger.warning(
                f"[curated RAG] even a single example exceeds the {self.max_tokens}-token "
                f"budget at depth {len(history)} — no RAG block for this step"
            )
        return ""


def build_curated_rag(args, directory, len_idx_target_idx, data_split="test", logger=None):
    """CuratedRag for this case, or None when --rag is not curated_pipeline.

    A disabled handle (missing DB / failed vector) is still returned rather than None so
    callers have one uniform object to ask; it simply yields empty hint blocks.
    """
    if getattr(args, "rag", "none") != "curated_pipeline":
        return None

    db_path = getattr(args, "curated_pipeline_db", DEFAULT_CURATED_DB)
    norm_stats = getattr(args, "curated_pipeline_norm_stats", DEFAULT_CURATED_NORM_STATS)

    if not db_path or not os.path.exists(db_path):
        if logger is not None:
            logger.warning(
                f"[curated RAG] corpus not found at {db_path!r} — RAG disabled for this "
                "case. Build it with rag_pipeline/build_curated_pipeline_db.py."
            )
        return CuratedRag("", None, logger=logger)

    vector = build_query_vector(
        directory, len_idx_target_idx, norm_stats, data_split=data_split, logger=logger
    )
    return CuratedRag(
        db_path,
        vector,
        top_k=getattr(args, "rag_topk", 3),
        max_tokens=getattr(args, "rag_max_tokens", DEFAULT_RAG_MAX_TOKENS),
        logger=logger,
    )
