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

    # Microsoft DMX models via the SSH tunnel (ssh -N -L 8000:127.0.0.1:8000 <user>@<dmx-vm-host>):
    python3 run_openai_task.py \
        --task Transform-by-output-target-schema \
        --model dmx-gpt-oss-120b \
        --mmtu_jsonl mmtu_smartbuilding_v2.jsonl

    # On Sol, with Ollama serving Qwen3:32B:
    python3 run_openai_task.py \
        --task Transform-by-output-target-schema \
        --model qwen3:32b \
        --mmtu_jsonl mmtu.jsonl

Then evaluate with:
    python3 evaluate.py mmtu.<model_tag>.result.jsonl
"""
import argparse
import collections
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
from llm.llm_models import (
    _ollama_base_url, _OLLAMA_READ_TIMEOUT,
    DMX_PREFIX, is_dmx_model, _DMX_BASE_URL, _REASONING_EFFORT,
)
import httpx


def is_ollama_model(model):
    return "qwen" in model.lower()


def is_thinking_model(model):
    # Mirrors LLMClient's _is_thinking_model: Qwen3 emits hidden reasoning
    # tokens unless told not to; Qwen2.5 does not.
    return "qwen3" in model.lower()


# Every HTTP status the client receives, counting the OpenAI SDK's silent retries too (a 429 that is
# retried and then succeeds never shows up in the results file, only here).
STATUS_COUNTS = {}
_status_lock = threading.Lock()


def _count_status(response):
    with _status_lock:
        STATUS_COUNTS[response.status_code] = STATUS_COUNTS.get(response.status_code, 0) + 1


def build_client(model, api_key, max_retries=2):
    if is_dmx_model(model):
        return OpenAI(
            base_url=_DMX_BASE_URL,
            api_key="unused",  # the proxy on the VM adds the real Azure token
            max_retries=max_retries,
            http_client=httpx.Client(
                timeout=httpx.Timeout(connect=60.0, read=_OLLAMA_READ_TIMEOUT, write=120.0, pool=60.0),
                event_hooks={"response": [_count_status]},
            ),
        )
    if is_ollama_model(model):
        return OpenAI(
            base_url=_ollama_base_url(),
            api_key="ollama",
            timeout=httpx.Timeout(connect=60.0, read=_OLLAMA_READ_TIMEOUT, write=120.0, pool=60.0),
        )
    return OpenAI(api_key=api_key)


class RateLimiter:
    """At most max_calls request STARTS per period seconds, shared by every worker thread (sliding window).
    Retries acquire too, so a burst of 429-retries can never exceed the budget either."""

    def __init__(self, max_calls, period):
        self.max_calls, self.period = max_calls, period
        self.calls = collections.deque()
        self.lock = threading.Lock()

    def acquire(self):
        while True:
            with self.lock:
                now = time.monotonic()
                while self.calls and now - self.calls[0] >= self.period:
                    self.calls.popleft()
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return
                wait = self.period - (now - self.calls[0])
            time.sleep(max(wait, 0.05))


LIMITER = None  # set in main() from --rate_limit_calls / --rate_limit_period


class AttemptLog:
    """One JSON line per HTTP attempt (full request, full response or error, status, latency) plus a live
    per-case tally of rate-limit (429) rejections, so every request and every faulting case is on record."""

    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.attempts = collections.Counter()          # case -> attempts so far
        self.cases = {}                                # case -> {"429": n, "other_errors": n, "attempts": n, "outcome": ...}
        self.n_ok = self.n_429 = self.n_other = 0

    def next_attempt(self, case):
        with self.lock:
            self.attempts[case] += 1
            return self.attempts[case]

    def record(self, case, attempt, status, latency, request, response=None, usage=None, error=None):
        line = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "case": case, "attempt": attempt, "status": status,
                "latency_s": round(latency, 2), "request": request, "response": response, "usage": usage, "error": error}
        with self.lock:
            with open(self.path, "a") as f:
                f.write(json.dumps(line) + "\n")
            c = self.cases.setdefault(case, {"attempts": 0, "429": 0, "other_errors": 0, "outcome": None, "ok_on_attempt": None})
            c["attempts"] += 1
            if status == 200:
                self.n_ok += 1
                c["ok_on_attempt"] = attempt
            elif status == 429:
                self.n_429 += 1
                c["429"] += 1
                print(f"[429] {case} rejected on attempt {attempt} (this case: {c['429']} x 429; run total: {self.n_429})", flush=True)
            else:
                self.n_other += 1
                c["other_errors"] += 1
                print(f"[error {status}] {case} attempt {attempt}: {str(error)[:120]}", flush=True)

    def finish(self, case, ok):
        with self.lock:
            c = self.cases.setdefault(case, {"attempts": 0, "429": 0, "other_errors": 0, "outcome": None, "ok_on_attempt": None})
            c["outcome"] = "ok" if ok else "gave_up"

    def status_line(self, done, total):
        with self.lock:
            faulting = [k for k, v in self.cases.items() if v["429"] and v["outcome"] is None]
            hit = sum(1 for v in self.cases.values() if v["429"])
            return (f"[monitor {time.strftime('%H:%M:%S')}] done {done}/{total} | attempts: {self.n_ok} ok, {self.n_429} x 429, "
                    f"{self.n_other} other | cases hit by a 429: {hit} | still retrying after a 429: {len(faulting)} {faulting[:6]}")

    def summary(self):
        with self.lock:
            hit = {k: v for k, v in self.cases.items() if v["429"]}
            recovered = sorted(k for k, v in hit.items() if v["outcome"] == "ok")
            gave_up = sorted(k for k, v in self.cases.items() if v["outcome"] == "gave_up")
            return {"attempts_ok": self.n_ok, "attempts_429": self.n_429, "attempts_other_errors": self.n_other,
                    "cases_hit_by_429": len(hit), "recovered_after_429": recovered, "gave_up": gave_up, "per_case": hit}


ATTEMPT_LOG = None  # set in main()


def _query_request(client, model, prompt, temperature=1.0, timeout=90, case_id=None):
    if LIMITER is not None:
        LIMITER.acquire()   # every attempt, including tenacity's retries
    attempt = ATTEMPT_LOG.next_attempt(case_id) if ATTEMPT_LOG is not None else 0
    t0 = time.time()
    kwargs = dict(
        model=model[len(DMX_PREFIX):] if is_dmx_model(model) else model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        timeout=timeout,
    )
    if is_dmx_model(model) and _REASONING_EFFORT:
        kwargs["reasoning_effort"] = _REASONING_EFFORT
    if is_thinking_model(model):
        # Ollama-specific: skip the reasoning/"thinking" pass so the full
        # response budget goes to the actual code, not hidden reasoning.
        kwargs["extra_body"] = {"think": False}
    request_record = {"model": model, "temperature": temperature, "messages": kwargs["messages"]}
    try:
        completion = client.with_options(timeout=timeout).chat.completions.create(**kwargs)
    except Exception as e:
        if ATTEMPT_LOG is not None:
            ATTEMPT_LOG.record(case_id, attempt, getattr(e, "status_code", None) or type(e).__name__, time.time() - t0,
                               request_record, error=str(e)[:800])
        raise
    if ATTEMPT_LOG is not None:
        u = completion.usage
        ATTEMPT_LOG.record(case_id, attempt, 200, time.time() - t0, request_record,
                           response=completion.choices[0].message.content,
                           usage={"prompt_tokens": u.prompt_tokens, "completion_tokens": u.completion_tokens} if u else None)
    return {
        "response": completion.choices[0].message.content,
        "prompt_tokens": completion.usage.prompt_tokens if completion.usage else None,
        "completion_tokens": completion.usage.completion_tokens if completion.usage else None,
        "time_taken": time.time() - t0,
    }


def parse_case_id(test_case):
    match = re.match(r"^length(\d+)_(\d+)$", test_case)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


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


def select_batch(rows, batch_size, batch_index):
    # Case IDs aren't contiguous within a length (MMTU's curated set skips
    # some of the raw benchmark's ~100 cases per length), so slicing by raw
    # numeric --id_start/--id_end (mcts_search.py's convention) would give
    # uneven batch sizes. Instead: sort by actual existing (length, case_id),
    # then slice by position -- guarantees exactly batch_size per batch
    # (remainder on the last one), independent of gaps.
    keyed = sorted(rows, key=lambda r: parse_case_id(json.loads(r["metadata"])["test_case"]) or (0, 0))
    start = batch_index * batch_size
    return keyed[start:start + batch_size]


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
    parser.add_argument("--rate_limit_calls", type=int, default=0,
                        help="With --rate_limit_period: at most this many requests START per period, across all workers "
                             "(0 = no limit). Retries count too. Also turns off the OpenAI SDK's own hidden retries so "
                             "every attempt goes through the limiter.")
    parser.add_argument("--rate_limit_period", type=float, default=30.0, help="Window length in seconds for --rate_limit_calls")
    parser.add_argument("--retry_attempts", type=int, default=6, help="Attempts per query before it is saved as an empty response")
    parser.add_argument("--retry_max_wait", type=float, default=30.0, help="Longest backoff (seconds) between attempts")
    parser.add_argument("--delay_seconds", type=float, default=0.0,
                        help="Seconds each worker waits after finishing a query before taking the next one. Without it every worker "
                             "fires its next request the instant one returns, which trips the proxy's rate limit (HTTP 429) at "
                             "10-20 workers; a few seconds staggers the requests.")
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N rows (smoke test)")
    parser.add_argument("--timeout", type=float, default=None, help="Per-request timeout in seconds (default: 90 for OpenAI, $TRANSCHEMA_OLLAMA_HTTP_TIMEOUT [3600s] for Ollama/Qwen models)")
    parser.add_argument("--batch_size", type=int, default=None, help="Cases per batch (use with --batch_index; sorted by actual existing case ID, not raw numeric range, since IDs aren't contiguous within a length)")
    parser.add_argument("--batch_index", type=int, default=None, help="0-indexed batch to run (use with --batch_size)")
    args = parser.parse_args()

    assert (args.batch_size is None) == (args.batch_index is None), "--batch_size and --batch_index must be used together"

    if is_dmx_model(args.model):
        # DMX models go through the SSH-tunnelled proxy on localhost:8000, which adds the
        # Azure token itself -- no API key here. Reasoning models need the long read timeout.
        timeout = args.timeout if args.timeout is not None else _OLLAMA_READ_TIMEOUT
    elif is_ollama_model(args.model):
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

    if args.batch_size is not None:
        n_batches = -(-len(rows) // args.batch_size)  # ceil
        assert 0 <= args.batch_index < n_batches, f"batch_index must be in [0, {n_batches}) for batch_size={args.batch_size} over {len(rows)} rows"
        rows = select_batch(rows, args.batch_size, args.batch_index)
        print(f"Batch {args.batch_index}/{n_batches - 1}: {len(rows)} rows")

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

    global LIMITER, query_request, ATTEMPT_LOG
    attempt_log_path = os.path.join(args.output_dir, f"attempts.{model_tag}.jsonl")
    ATTEMPT_LOG = AttemptLog(attempt_log_path)
    print(f"Every request/response is logged to {attempt_log_path}", flush=True)
    if args.rate_limit_calls > 0:
        LIMITER = RateLimiter(args.rate_limit_calls, args.rate_limit_period)
        print(f"Rate limit: at most {args.rate_limit_calls} request starts per {args.rate_limit_period:.0f}s "
              f"(shared by all {args.n_parallel} workers; retries included)")
    query_request = retry(wait=wait_random_exponential(max=args.retry_max_wait, multiplier=2),
                          stop=stop_after_attempt(args.retry_attempts))(_query_request)
    client = build_client(args.model, args.api_key, max_retries=0 if args.rate_limit_calls > 0 else 2)
    file_lock = threading.Lock()
    queue = Queue()
    for row in todo:
        queue.put(row)
    n_gave_up = [0]

    pbar = tqdm(total=len(todo), desc=f"Querying {args.model}", ncols=100)

    def worker():
        while True:
            try:
                row = queue.get_nowait()
            except Exception:
                return
            case_id = json.loads(row["metadata"]).get("test_case")
            try:
                result = query_request(client, args.model, row["prompt"], args.temperature, timeout, case_id)
                response = result.get("response", "")
                prompt_tokens = result.get("prompt_tokens")
                completion_tokens = result.get("completion_tokens")
                time_taken = result.get("time_taken")
            except Exception as e:
                print(f"Failed query: {e}")
                response, prompt_tokens, completion_tokens, time_taken = "", None, None, None
                with file_lock:
                    n_gave_up[0] += 1

            if ATTEMPT_LOG is not None:
                ATTEMPT_LOG.finish(case_id, bool(response))
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
            if args.delay_seconds and not queue.empty():
                time.sleep(args.delay_seconds)

    stop_monitor = threading.Event()

    def monitor():
        while not stop_monitor.wait(60):
            print(ATTEMPT_LOG.status_line(pbar.n, len(todo)), flush=True)

    threading.Thread(target=monitor, daemon=True).start()
    threads = [threading.Thread(target=worker) for _ in range(args.n_parallel)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    pbar.close()

    stop_monitor.set()
    summ = ATTEMPT_LOG.summary()
    with open(os.path.join(args.output_dir, f"rate_limit_cases.{model_tag}.json"), "w") as f:
        json.dump(summ, f, indent=2)
    print(f"\nRate-limit monitor: {summ['attempts_429']} rejected attempts (429) across {summ['cases_hit_by_429']} cases; "
          f"{len(summ['recovered_after_429'])} recovered after retrying, {len(summ['gave_up'])} gave up {summ['gave_up']}; "
          f"{summ['attempts_ok']} successful attempts, {summ['attempts_other_errors']} other errors", flush=True)
    if STATUS_COUNTS:
        print(f"\nHTTP responses the client received (every attempt, incl. silent retries): {dict(sorted(STATUS_COUNTS.items()))}"
              f"  -> rate-limited (429): {STATUS_COUNTS.get(429, 0)}")
    print(f"\nQueries that gave up after all retries (saved as empty responses, retried on a rerun): {n_gave_up[0]} of {len(todo)}")
    print(f"\nDone. Results written to {output_file}")
    print(f"Evaluate with:\n    python3 evaluate.py {output_file}")


if __name__ == "__main__":
    main()
