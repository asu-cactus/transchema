"""Standalone entrypoint to run a single MMTU task against the OpenAI API,
or a local Ollama-hosted model (e.g. Qwen3:32B on Sol).

Bypasses two issues in inference.py:
  - the `openai` provider constructs OpenAI(api_base=..., api_version=...),
    which are not valid kwargs for openai>=1.0's OpenAI client (only
    AzureOpenAI takes api_version; base_url replaces api_base).
  - `-i/--input_file` is unimplemented, so inference.py always queries the
    full ~28K-row MMTU dataset instead of a single task's subset.

Qwen models route to a local Ollama server instead of OpenAI's cloud API --
same routing convention (respects $OLLAMA_HOST, long default read timeout via
$TRANSCHEMA_OLLAMA_HTTP_TIMEOUT) as llm/llm_models.py's LLMClient, used by
Langraph/mcts_search.py. Reuses that module's base-URL resolution directly
rather than duplicating it, but does not import LLMClient itself (it eagerly
downloads a HuggingFace tokenizer in __init__, which this script doesn't need).

Usage:
    python3 run_openai_task.py \
        --task Transform-by-output-target-schema \
        --model gpt-4.1-mini \
        --api_key $OPENAI_API_KEY \
        --mmtu_jsonl mmtu.jsonl

    # On Sol, with Ollama serving Qwen3:32B:
    python3 run_openai_task.py \
        --task Transform-by-output-target-schema \
        --model qwen3:32b \
        --mmtu_jsonl mmtu.jsonl

Then evaluate with:
    python3 evaluate.py mmtu.<model_tag>.result.jsonl
"""
import argparse
import json
import os
import re
import sys
import threading
import time
from queue import Queue

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm import tqdm

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from llm.llm_models import _ollama_base_url, _OLLAMA_READ_TIMEOUT
import httpx


def is_ollama_model(model):
    return "qwen" in model.lower()


def is_thinking_model(model):
    # Mirrors LLMClient's _is_thinking_model: Qwen3 emits hidden reasoning
    # tokens unless told not to; Qwen2.5 does not.
    return "qwen3" in model.lower()


def build_client(model, api_key):
    if is_ollama_model(model):
        return OpenAI(
            base_url=_ollama_base_url(),
            api_key="ollama",
            timeout=httpx.Timeout(connect=60.0, read=_OLLAMA_READ_TIMEOUT, write=120.0, pool=60.0),
        )
    return OpenAI(api_key=api_key)


@retry(wait=wait_random_exponential(max=30, multiplier=2), stop=stop_after_attempt(6))
def query_request(client, model, prompt, temperature=1.0, timeout=90):
    t0 = time.time()
    kwargs = dict(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        timeout=timeout,
    )
    if is_thinking_model(model):
        # Ollama-specific: skip the reasoning/"thinking" pass so the full
        # response budget goes to the actual code, not hidden reasoning.
        kwargs["extra_body"] = {"think": False}
    completion = client.with_options(timeout=timeout).chat.completions.create(**kwargs)
    return {
        "response": completion.choices[0].message.content,
        "prompt_tokens": completion.usage.prompt_tokens if completion.usage else None,
        "completion_tokens": completion.usage.completion_tokens if completion.usage else None,
        "time_taken": time.time() - t0,
    }


def load_task_rows(mmtu_jsonl_path, task, dataset=None, length=None):
    rows = []
    with open(mmtu_jsonl_path) as f:
        for line in f:
            row = json.loads(line)
            if row.get("task") != task:
                continue
            if dataset is not None and row.get("dataset") != dataset:
                continue
            if length is not None:
                test_case = json.loads(row["metadata"]).get("test_case", "")
                match = re.match(r"^length(\d+)_", test_case)
                if not match or int(match.group(1)) != length:
                    continue
            rows.append(row)
    return rows


def load_done_metadata(output_file):
    done = set()
    if not os.path.exists(output_file):
        return done
    with open(output_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("response"):
                done.add(row["metadata"])
    return done


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--task", default="Transform-by-output-target-schema", help="MMTU task name to filter to")
    parser.add_argument("--dataset", default=None, help="Optional sub-dataset to filter to (e.g. github-pipelines)")
    parser.add_argument("--length", type=int, default=None, help="Optional pipeline-length bucket to filter to (parsed from test_case, e.g. 1 for length1_*)")
    parser.add_argument("--model", default="gpt-4.1-mini", help="OpenAI model name")
    parser.add_argument("--api_key", default=os.environ.get("OPENAI_API_KEY"), help="OpenAI API key (defaults to $OPENAI_API_KEY)")
    parser.add_argument("--mmtu_jsonl", default="mmtu.jsonl", help="Path to the downloaded MMTU dataset jsonl")
    parser.add_argument("--output_dir", default=".", help="Directory to write the result jsonl to")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--n_parallel", type=int, default=4, help="Number of concurrent request threads")
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N rows (smoke test)")
    parser.add_argument("--timeout", type=float, default=None, help="Per-request timeout in seconds (default: 90 for OpenAI, $TRANSCHEMA_OLLAMA_HTTP_TIMEOUT [3600s] for Ollama/Qwen models)")
    args = parser.parse_args()

    if is_ollama_model(args.model):
        # Ollama uses a placeholder key -- no real OpenAI credentials needed.
        timeout = args.timeout if args.timeout is not None else _OLLAMA_READ_TIMEOUT
    else:
        assert args.api_key, "No API key found. Pass --api_key or set OPENAI_API_KEY."
        timeout = args.timeout if args.timeout is not None else 90
    assert os.path.exists(args.mmtu_jsonl), f"{args.mmtu_jsonl} not found. Download the MMTU dataset first."

    rows = load_task_rows(args.mmtu_jsonl, args.task, args.dataset, args.length)
    scope = f"task={args.task}"
    if args.dataset:
        scope += f", dataset={args.dataset}"
    if args.length is not None:
        scope += f", length={args.length}"
    print(f"Loaded {len(rows)} rows for {scope}")
    assert rows, f"No rows found for {scope}. Check the task/dataset name."

    if args.limit is not None:
        rows = rows[:args.limit]
        print(f"Limiting to first {len(rows)} rows")

    # Model names can contain dots (e.g. gpt-4.1-mini) or colons (Ollama tags
    # like qwen3:32b), which would break evaluate.py's
    # `basename.split(".")[-3]` model-name parsing if used directly in the
    # filename, so sanitize for the filename only.
    model_tag = args.model.replace(".", "-").replace(":", "-")
    os.makedirs(args.output_dir, exist_ok=True)
    output_file = os.path.join(args.output_dir, f"mmtu.{model_tag}.result.jsonl")

    done_metadata = load_done_metadata(output_file)
    if done_metadata:
        print(f"Resuming: {len(done_metadata)} rows already completed in {output_file}")

    todo = [row for row in rows if row["metadata"] not in done_metadata]
    print(f"{len(todo)} rows left to query")
    if not todo:
        print("Nothing to do.")
        return

    client = build_client(args.model, args.api_key)
    file_lock = threading.Lock()
    queue = Queue()
    for row in todo:
        queue.put(row)

    pbar = tqdm(total=len(todo), desc=f"Querying {args.model}", ncols=100)

    def worker():
        while True:
            try:
                row = queue.get_nowait()
            except Exception:
                return
            try:
                result = query_request(client, args.model, row["prompt"], args.temperature, timeout)
                response = result.get("response", "")
                prompt_tokens = result.get("prompt_tokens")
                completion_tokens = result.get("completion_tokens")
                time_taken = result.get("time_taken")
            except Exception as e:
                print(f"Failed query: {e}")
                response, prompt_tokens, completion_tokens, time_taken = "", None, None, None

            row_out = dict(row)
            row_out["response"] = response
            row_out["prompt_tokens"] = prompt_tokens
            row_out["completion_tokens"] = completion_tokens
            row_out["time_taken"] = time_taken
            row_out["model_name"] = args.model

            with file_lock:
                with open(output_file, "a") as f:
                    f.write(json.dumps(row_out) + "\n")
            pbar.update(1)
            queue.task_done()

    threads = [threading.Thread(target=worker) for _ in range(args.n_parallel)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    pbar.close()

    print(f"\nDone. Results written to {output_file}")
    print(f"Evaluate with:\n    python3 evaluate.py {output_file}")


if __name__ == "__main__":
    main()
