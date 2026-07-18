"""CLI runner for SQLMorpher on the same Auto-Pipeline benchmark used by
Transchema's `critique_data.py`, with matching flags (--len_id, --max_len_id,
--target_id, --max_target_id, --cases, --model, --benchmark, --log-dir, ...).

Example:
    python run_auto_pipeline.py --len_id 1 --target_id 10 --max_target_id 20 \
        --model qwen2.5-coder:32b --benchmark github

    python run_auto_pipeline.py --cases 1_17 4_31 --model gpt-4.1-mini
"""

import argparse
import os
import sys
import traceback
import urllib.error
import urllib.request

import gpt
from auto_pipeline_join import main as run_case
from llm_client import _is_ollama_model, _OLLAMA_BASE_URL
from prepare_transchema_json import build_grouped_json, ensure_cases_available
from util import create_connection

_BENCHMARK_DIRS = {
    "github": "../autopipeline-benchmarks/github-pipelines",
    "monteprep": "../autopipeline-benchmarks/monteprep-pipelines",
}


def get_parser():
    parser = argparse.ArgumentParser(
        description="Run SQLMorpher on the Transchema Auto-Pipeline benchmark"
    )
    parser.add_argument("--len_id", type=int, default=1, help="Len ID")
    parser.add_argument("--max_len_id", type=int, default=1, help="Max Len ID")
    parser.add_argument("--target_id", type=int, default=1, help="Target ID (start)")
    parser.add_argument("--max_target_id", type=int, default=1, help="Max Target ID (end, inclusive)")
    parser.add_argument(
        "--cases",
        type=str,
        nargs="+",
        default=None,
        help="Explicit list of case IDs to run, e.g. --cases 1_17 4_31. "
             "Overrides --len_id / --target_id / --max_target_id.",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="github",
        choices=["github", "monteprep"],
        help="Benchmark dataset: 'github' or 'monteprep' (same choice as critique_data.py).",
    )
    parser.add_argument(
        "--template_option",
        type=int,
        default=4,
        help="SQLMorpher prompt template option (4 = Auto-Pipeline join template).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.environ.get("SQLMORPHER_MODEL", "gpt-4-1106-preview"),
        help="Model name: an OpenAI model (e.g. gpt-4.1-mini) or a local Ollama "
             "model (e.g. qwen2.5-coder:32b, qwen3:8b, deepseek-r1:32b, mixtral:8x7b).",
    )
    parser.add_argument(
        "--transchema-data-dir",
        type=str,
        default="../data",
        help="Path to Transchema's data/ directory (for chatgpt_*_ms.json).",
    )
    parser.add_argument(
        "--benchmark-dir",
        type=str,
        default=None,
        help="Path to the Auto-Pipeline case folders "
             "(default: ../autopipeline-benchmarks/{benchmark}-pipelines).",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs-sqlmorpher",
        help="Directory to write run logs to.",
    )
    return parser


def _check_ollama_reachable(timeout=5):
    """Pings the Ollama server's /api/tags endpoint. Returns (ok, message)."""
    base = _OLLAMA_BASE_URL.rsplit("/v1", 1)[0]
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=timeout) as resp:
            return resp.status == 200, None
    except urllib.error.URLError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def main():
    args = get_parser().parse_args()

    # Fail fast with a clear message if the model needs Ollama and it isn't
    # reachable, instead of hanging silently through several minutes of
    # connection retries (which can look like the terminal "crashed").
    if _is_ollama_model(args.model):
        ok, err = _check_ollama_reachable()
        if not ok:
            print(
                f"ERROR: Ollama server not reachable at {_OLLAMA_BASE_URL} for model "
                f"'{args.model}'.\n"
                f"  Details: {err}\n"
                "  Start it first, e.g.:\n"
                "    ollama serve &\n"
                "    ollama pull " + args.model + "\n"
                "  On CHPC: if you're on a login node, run this inside an interactive "
                "job (e.g. `salloc` / `srun --pty bash`) instead — login nodes often "
                "kill or throttle long-running/foreground processes, which can look "
                "like the terminal 'crashing' with no Python error at all."
            )
            sys.exit(1)

    # Route the configured model through gpt.py's LLM client (OpenAI or Ollama).
    os.environ["SQLMORPHER_MODEL"] = args.model
    gpt._client = gpt.LLMClient(model=args.model, tracker=gpt.default_tracker, logger=gpt._logger)

    os.makedirs(args.log_dir, exist_ok=True)

    benchmark_dir = args.benchmark_dir or _BENCHMARK_DIRS[args.benchmark]
    # Cheap: just loads/copies Transchema's flat JSON into grouped form, no
    # disk scanning of the (700-case, 3.4GB) benchmark folder.
    json_file_path = build_grouped_json(args.benchmark, args.transchema_data_dir)

    # SQLMorpher executes generated SQL against a real Postgres instance, unlike
    # Transchema's Python-pipeline path. Fail fast with a clear message instead
    # of retrying/erroring per-case if Postgres isn't reachable.
    try:
        create_connection().close()
    except Exception as e:
        print(
            "ERROR: could not connect to Postgres. SQLMorpher needs a running "
            "Postgres server to execute generated SQL.\n"
            f"  Details: {e}\n"
            "  Configure the connection via env vars (defaults shown):\n"
            "    SQLMORPHER_PG_HOST=localhost SQLMORPHER_PG_PORT=5432 "
            "SQLMORPHER_PG_DBNAME=postgres SQLMORPHER_PG_USER=postgres "
            "SQLMORPHER_PG_PASSWORD=***\n"
            "  On CHPC, start/enable a local Postgres (e.g. via a module, "
            "conda-installed postgres, or a container) before rerunning."
        )
        sys.exit(1)

    if args.cases:
        case_pairs = [(int(c.split("_")[0]), int(c.split("_")[1])) for c in args.cases]
    else:
        case_pairs = [
            (length, tid)
            for length in range(args.len_id, args.max_len_id + 1)
            for tid in range(args.target_id, args.max_target_id + 1)
        ]

    # Case IDs in this benchmark are NOT contiguous (e.g. length1_* only has
    # 1, 2, 5, 7, 8, 12, 14, 15, 17, 19, 25, ...) and the metadata JSON only
    # covers a subset of the cases that actually exist on disk. Rather than
    # scanning the whole (700-case, 3.4GB) benchmark folder, only synthesize
    # metadata for the specific cases requested here — one folder at a time.
    unresolved = ensure_cases_available(json_file_path, case_pairs, benchmark_dir)

    valid_case_pairs = [
        (length, tid) for length, tid in case_pairs if f"{length}_{tid}" not in unresolved
    ]

    if unresolved:
        print(f"Skipping {len(unresolved)} case(s) not found in the dataset or on disk: {sorted(unresolved)}")
    if not valid_case_pairs:
        print("No valid cases to run. Exiting.")
        sys.exit(1)

    case_pairs = valid_case_pairs
    print(f"Model: {args.model} | Benchmark: {args.benchmark} | Cases: {case_pairs}")

    succeeded, failed = 0, 0
    for length, case_id in case_pairs:
        case_path = f"{length}_{case_id}"
        print(f"\n=== Running case {case_path} ===")
        try:
            run_case(
                json_file_path,
                args.template_option,
                case_id,
                case_id,
                length,
                benchmark_dir=benchmark_dir,
            )
            succeeded += 1
        except Exception:
            failed += 1
            print(f"Case {case_path} failed:\n{traceback.format_exc()}")

    print(f"\nDone. {succeeded} case(s) succeeded, {failed} case(s) failed.")
    print("Token usage / cost summary:", gpt.token_usage_summary())


if __name__ == "__main__":
    main()
