"""
Standalone script: generate code for a given operation history via the
MCTS simulate prompt, execute it, and score against the ground truth.

Usage:
    python run_simulate_validate.py
"""

import os, sys, logging, subprocess, tempfile, traceback

ROOT = "/home/asurite.ad.asu.edu/jrtandel/transchema"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "eval_score"))
sys.path.insert(0, os.path.join(ROOT, "Langraph"))
os.chdir(ROOT)

import pandas as pd
from Langraph.nodes import get_prompt, query_gpt, _score_and_validate_output
from llm.llm_models import LLMClient, TokenUsageTracker

# ── case config ───────────────────────────────────────────────────────────────

CASE        = "length1_9"
LENGTH      = 1
ID          = 9
PIPELINES_DIR = "autopipeline-benchmarks/github-pipelines"
CASE_DIR      = f"{PIPELINES_DIR}/{CASE}"
SOURCE_FILE   = f"{CASE_DIR}/test_0.csv"
TARGET_FILE   = f"{CASE_DIR}/target.csv"
OUTPUT_CSV    = f"{CASE_DIR}/target_simulate_test.csv"

# Operation history to test
OPERATION_HISTORY = [
    "GROUP_BY/AGGREGATE : group_by=[Source1_9_0.zipcode] "
    "aggregations=[sum(Source1_9_0.AGI_STUB), sum(Source1_9_0.N1), sum(Source1_9_0.A00100)]",
    "NO_MORE_OPERATION",
]

# ── build minimal config object ───────────────────────────────────────────────

class SimpleConfig:
    pass

df_src = pd.read_csv(SOURCE_FILE, index_col=0)
df_tgt = pd.read_csv(TARGET_FILE)
tgt_cols   = [c for c in df_tgt.columns if not c.startswith("Unnamed")]
tgt_schema = ", ".join(tgt_cols)
tgt_schema_types = ", ".join(
    f"{c}: {str(df_tgt[c].dtype)}" for c in tgt_cols
)
tgt_samples = df_tgt[tgt_cols].head(5).to_string(index=False)

src_schema = ", ".join(df_src.columns.tolist())
src_info   = (
    f"Source0: {CASE}/test_0.csv\n"
    f"  Schema: {src_schema}\n"
    f"  Rows: {len(df_src)}"
)

token_tracker = TokenUsageTracker()
llm_client = LLMClient(model="gpt-4.1-mini", tracker=token_tracker, logger=logging.getLogger("llm"))

cfg = SimpleConfig()
cfg.target_data_name            = CASE
cfg.target_data_schema          = tgt_schema
cfg.target_data_schema_with_types = tgt_schema_types
cfg.target_samples              = tgt_samples
cfg.file_count                  = 1
cfg.source_data_name_list       = [f"Source1_{ID}_0"]
cfg.source_data_schema_list     = [src_schema]
cfg.directory                   = PIPELINES_DIR
cfg.len_idx_target_idx          = f"1_{ID}"
cfg.target_perc                 = 1.0
cfg.is_perc                     = False
cfg.target_length               = len(df_tgt)
cfg.source_length               = len(df_src)
cfg.fd_flag                     = False
cfg.hint_source                 = ""
cfg.llm_client                  = llm_client
cfg.q_count                     = {"total": 0, "in_task": 0}
cfg.logger                      = logging.getLogger("simulate_test")
cfg.cost_summary                = [token_tracker.cost_summary()]  # initial snapshot required by query_gpt
cfg.token_tracker               = token_tracker
cfg.model                       = "gpt-4.1-mini"
cfg.token_limit                 = 8192
cfg.source_information          = src_info
cfg.static_hints                = True
cfg.fd_hints                    = ""
cfg.mcts_critique_mode          = "none"
cfg.reward_mode                 = "score"
cfg.intermediate_materialization = False
cfg.data_split                  = "test"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# ── build fake state ──────────────────────────────────────────────────────────

state = {
    "config": cfg,
    "local_rag_db_path": "",
    "iteration": 0,
}

# ── generate code ─────────────────────────────────────────────────────────────

print("=" * 60)
print(f"Case:              {CASE}")
print(f"Operation history: {OPERATION_HISTORY}")
print("=" * 60)
print("\nGenerating code via simulate prompt...")

MAX_TRIALS = 3
error_str  = ""
final_code = None

for trial in range(MAX_TRIALS):
    try:
        prompt = get_prompt(
            prompt_type="python_script",
            max_tokens=cfg.token_limit,
            model=cfg.model,
            allowed_operation_list=["JOIN", "GROUP_BY/AGGREGATE", "UNION", "NO_MORE_OPERATION"],
            operation_history=OPERATION_HISTORY,
            target_data_name=cfg.target_data_name,
            target_data_schema=cfg.target_data_schema,
            target_data_schema_with_types=cfg.target_data_schema_with_types,
            target_samples=cfg.target_samples,
            file_count=cfg.file_count,
            source_data_name_list=cfg.source_data_name_list,
            source_data_schema_list=cfg.source_data_schema_list,
            directory=cfg.directory,
            len_idx_target_idx=cfg.len_idx_target_idx,
            target_perc=cfg.target_perc,
            is_perc=cfg.is_perc,
            target_length=cfg.target_length,
            source_length=cfg.source_length,
            error_string=error_str,
            csv_save_path=OUTPUT_CSV,
            hint_source=cfg.hint_source,
            static_hints=cfg.static_hints,
            fd_flag=int(cfg.fd_flag),
            nth_intermediate_step=0,
            intermediate_scores={},
            is_final=True,
            data_split=cfg.data_split,
            rag_hints="",
        )
    except Exception:
        print(f"[Trial {trial}] get_prompt failed:\n{traceback.format_exc()}")
        break

    res = query_gpt(
        cfg.llm_client,
        cfg.model,
        prompt,
        cfg.q_count,
        cfg.logger,
        cfg.cost_summary,
        cfg.token_tracker,
        type="MCTS Simulate Python",
    )
    response = res[0]
    print(f"\n[Trial {trial}] LLM response:\n{response}\n")

    # extract code block
    import re
    match = re.search(r"```[Pp]ython\s*(.*?)```", response, re.DOTALL)
    if not match:
        print(f"[Trial {trial}] No code block found, retrying...")
        error_str = "No Python code block found in response."
        continue

    code = match.group(1).strip()
    print(f"[Trial {trial}] Extracted code:\n{code}\n")

    # execute
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_script = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_script],
            capture_output=True, text=True, cwd=ROOT, timeout=60
        )
        os.unlink(tmp_script)
    except subprocess.TimeoutExpired:
        os.unlink(tmp_script)
        error_str = "Execution timed out after 60s."
        print(f"[Trial {trial}] Timeout.")
        continue

    if result.returncode != 0:
        error_str = result.stderr.strip()
        print(f"[Trial {trial}] Execution error:\n{error_str}")
        continue

    # success
    final_code = code
    print(f"[Trial {trial}] Code executed successfully. Output: {OUTPUT_CSV}")
    break

# ── validate ──────────────────────────────────────────────────────────────────

if final_code is None:
    print("\nFailed to generate executable code after all trials.")
    sys.exit(1)

if not os.path.exists(OUTPUT_CSV):
    print(f"\nOutput CSV not found at {OUTPUT_CSV}")
    sys.exit(1)

print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)

df_out = pd.read_csv(OUTPUT_CSV)
df_gt  = pd.read_csv(TARGET_FILE)
print(f"Generated output: {df_out.shape}  cols={list(df_out.columns)}")
print(f"Ground truth:     {df_gt.shape}   cols={[c for c in df_gt.columns if not c.startswith('Unnamed')]}")
print(f"\nGenerated head:\n{df_out.head(5).to_string(index=False)}")

score, is_correct = _score_and_validate_output(
    OUTPUT_CSV, TARGET_FILE,
    validation_mode="autopipeline",
    reward_mode="score",
)
print(f"\nScore:      {score:.4f}")
print(f"Is correct: {is_correct}  (threshold = 0.9)")
