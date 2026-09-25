# Curated-Pipeline RAG: Running It and Integrating It Elsewhere

Branch: `best_score_script_mcts`

`curated_pipeline` is a RAG mode for MCTS schema-transformation search: instead of
schema-embedding similarity (the older `global` mode), it retrieves few-shot examples by
**prefix-matching** the current partial operation plan against a static library of 656
deduplicated pipelines, breaking ties by **cosine similarity on an 8-dimensional
structural feature vector** computed from the actual source/target tables.

## 1. Files needed -- no setup required

Nothing needs to be built or configured. These 4 files are sufficient to run as-is:

| File | What it is |
|---|---|
| `rag_pipeline/db/curated_pipeline_656.db` | The corpus: SQLite table of 656 deduplicated pipelines. |
| `rag_pipeline/db/curated_pipeline_features.norm_stats.json` | Per-dimension mean/std the corpus vectors were normalized with -- required so a new query vector lands in the same space. |
| `rag_pipeline/feature_extractor.py` | Code that computes a case's 8-dim query vector and normalizes it. |
| `rag_pipeline/local_rag_db.py` | Code that queries the `.db` (prefix-match + cosine-similarity tie-break) and formats the hint text. |

Both `.py` files are self-contained -- their only import outside the standard library is
`pandas`, nothing else from this repo. The `.db`/`.json` alone aren't runnable without
the two modules that know how to read them, so all 4 need to travel together (placing
all 4 into one `rag_pipeline/` folder in the target environment, matching this repo's
layout, is the simplest way to keep the imports in Section 3 resolving unchanged).

(The one-time build step that *produced* these two data files,
`rag_pipeline/build_curated_pipeline_db.py`, is only needed if the corpus itself has to
change later -- not when only consuming the existing 656-pipeline corpus.)

## 2. Sample command to run with it

A single case (length 2, case 5), same flags this session's experiments used:

```bash
source env/bin/activate
python3 Langraph/mcts_search.py \
    --model              gpt-4.1-mini \
    --token_limit        12000 \
    --source_length      3 \
    --target_length      3 \
    --mcts_iterations    40 \
    --early_stopping      0 \
    --mcts_critique_mode  simulate \
    --validation          autopipeline \
    --reward              det_score_value \
    --simulation           pipeline \
    --rag                  curated_pipeline \
    --curated_pipeline_db          rag_pipeline/db/curated_pipeline_656.db \
    --curated_pipeline_norm_stats  rag_pipeline/db/curated_pipeline_features.norm_stats.json \
    --data_split          training \
    --length               2 \
    --id_start             5 \
    --id_end               5 \
    --experiment_name     curated_pipeline_demo_l2_c5 \
    --log_dir             logs_langraph/curated_pipeline_demo/cases_c5 \
    --result_dir          results_langraph/curated_pipeline_demo
```