"""
Analyze input/output token usage for MCTS experiments.
Groups by (sim_type, length) across all relevant directories.
Outputs TSV suitable for copy-paste into Google Sheets.
"""

import os
import re
import ast
import sys
from collections import defaultdict

COST_RE = re.compile(r"Cost of the query\s*:\s*(\{.*\})")
FILE_RE = re.compile(r"^(\d+)_target(\d+)_.*\.log$")

# Map directory name -> (sim_type, length)
DIR_MAP = {
    "mcts_pipeline_10cent_len1_retry": ("pipeline", 1),
    "mcts_pipeline_10cent_len4_retry": ("pipeline", 4),
    "mcts_pipeline_10cent_len9_retry": ("pipeline", 9),
    "mcts_operator_10cent_len1_retry": ("operator", 1),
    "mcts_operator_10cent_len4_retry": ("operator", 4),
    "mcts_operator_10cent_len9_retry": ("operator", 9),
}


def extract_tokens_from_file(filepath):
    prompt_total = 0
    completion_total = 0
    with open(filepath, "r", errors="replace") as f:
        for line in f:
            m = COST_RE.search(line)
            if not m:
                continue
            try:
                cost_dict = ast.literal_eval(m.group(1))
                for model_data in cost_dict.get("detailed_cost", {}).values():
                    prompt_total += model_data.get("prompt_tokens", 0)
                    completion_total += model_data.get("completion_tokens", 0)
            except Exception:
                pass
    return prompt_total, completion_total


def collect_cases(root_dir):
    """
    Returns: dict[(sim_type, length, case_id)] -> [prompt_tokens, completion_tokens]
    """
    cases = defaultdict(lambda: [0, 0])

    for dirname, (sim_type, length) in DIR_MAP.items():
        dirpath = os.path.join(root_dir, dirname)
        if not os.path.isdir(dirpath):
            print(f"  WARNING: directory not found: {dirpath}", flush=True)
            continue
        for fname in os.listdir(dirpath):
            m = FILE_RE.match(fname)
            if not m:
                continue
            case_id = int(m.group(2))
            fpath = os.path.join(dirpath, fname)
            prompt, completion = extract_tokens_from_file(fpath)
            cases[(sim_type, length, case_id)][0] += prompt
            cases[(sim_type, length, case_id)][1] += completion

    return cases


def analyze(root_dir):
    print(f"Scanning: {root_dir}\n", flush=True)
    cases = collect_cases(root_dir)

    if not cases:
        print("No log files found.")
        return

    # Group by (sim_type, length)
    groups = defaultdict(list)
    for (sim_type, length, case_id), (prompt, completion) in cases.items():
        groups[(sim_type, length)].append((case_id, prompt, completion))

    header = [
        "Sim Type", "Length", "Cases",
        "Highest Case", "Highest Input Tokens", "Highest Output Tokens", "Highest Total Tokens",
        "Lowest Case", "Lowest Input Tokens", "Lowest Output Tokens", "Lowest Total Tokens",
        "Avg Input Tokens", "Avg Output Tokens", "Avg Total Tokens",
    ]
    rows = []

    for (sim_type, length) in sorted(groups.keys(), key=lambda x: (x[0], x[1])):
        entries = groups[(sim_type, length)]
        n = len(entries)

        total_costs = [(p + c, cid, p, c) for cid, p, c in entries]
        total_costs.sort()

        nonzero = [x for x in total_costs if x[0] > 0]
        lowest = nonzero[0] if nonzero else total_costs[0]
        highest = total_costs[-1]

        avg_prompt = sum(p for _, p, _ in entries) / n
        avg_completion = sum(c for _, _, c in entries) / n
        avg_total = avg_prompt + avg_completion

        rows.append([
            sim_type, length, n,
            f"case {highest[1]}", highest[2], highest[3], highest[0],
            f"case {lowest[1]}", lowest[2], lowest[3], lowest[0],
            round(avg_prompt, 1), round(avg_completion, 1), round(avg_total, 1),
        ])

    print("\t".join(header))
    for row in rows:
        print("\t".join(str(x) for x in row))


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "logs_langraph"
    if not os.path.isabs(root):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), root)
    analyze(root)
