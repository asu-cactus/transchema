import ast
import os
import sys
import pandas as pd
import json
from pandas.testing import assert_frame_equal
import numpy as np
from typing import Dict, Tuple, List
import random
from datetime import datetime

# transchema repo root (four levels up from BAT/src/utils/evaluator.py) — needed
# to reach the shared validation/ package used by Langraph/mcts_search.py's
# --validation autopipeline path, so BAT stays consistent with that scoring.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from validation.hard_match import compare_tables_matching


def drop_leading_index_col_if_present(df: pd.DataFrame) -> pd.DataFrame:
    """Drop the first column only if it's actually a throwaway pandas index
    column (unnamed, or literally "Unnamed: 0") -- true for every
    github-pipelines/monteprep-pipelines CSV (hence the previous unconditional
    `.iloc[:, 1:]` at this file's two call sites), but NOT true for
    smart_building's CSVs, whose first column is real data (e.g. CST/date/
    season). Blindly dropping it there would silently corrupt every row.
    Mirrors src/utils/csv_io.py's version -- duplicated (not imported) since
    this file runs as a bare script (`python3 src/utils/evaluator.py`, not
    `-m src.utils.evaluator`), so BAT's own directory isn't reliably on
    sys.path for a `from src.utils...` import to resolve.
    """
    if len(df.columns) > 0:
        first_col = str(df.columns[0])
        if first_col == "" or first_col.startswith("Unnamed:"):
            return df.drop(columns=df.columns[0])
    return df


def parse_llm_logs(log_file_path: str) -> List[Dict]:
    """Parse JSONL log file and return list of log entries."""
    logs = []
    if not os.path.exists(log_file_path):
        return logs
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
    except Exception as e:
        print(f"Warning: Failed to parse LLM logs from {log_file_path}: {e}")
    return logs

def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """Calculate API cost based on token usage and model."""
    pricing = {
        "gpt-4.1-mini": {"input": 0.15 / 1e6, "output": 0.60 / 1e6},
        "gpt-4o": {"input": 3.0 / 1e6, "output": 6.0 / 1e6},
        "o4-mini": {"input": 2.0 / 1e6, "output": 8.0 / 1e6},
    }
    if model not in pricing:
        return 0.0
    rates = pricing[model]
    return (prompt_tokens * rates["input"]) + (completion_tokens * rates["output"])

global_accuracy = {
    "total_samples": 0,
    "correct_total": 0
}
global_column_similarity = {
    "total_similarity": 0.0,
    "total_samples": 0
}
case_results = []  # Track results for CSV output

def read_csv_files(folder_path, folder_name):
    table_dict = {}
    if folder_name == "auto_pipeline":
        for file_name in os.listdir(folder_path):
            # Skip training files and any target*.csv variant — the folder also
            # holds answer-like artifacts from other methods' prior runs
            # (target_multisource.csv, target_multisource_mcts.csv, etc.); these
            # must never be exposed to the executed script as a usable source.
            if (file_name.lower().endswith('.csv')
                    and not file_name.startswith('training')
                    and not file_name.startswith('target')):
                key = os.path.splitext(file_name)[0]
                file_path = os.path.join(folder_path, file_name)
                table_dict[key] = drop_leading_index_col_if_present(pd.read_csv(file_path))
    elif folder_name == "buildings":
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith('.csv') and not file_name.startswith('target'):
                file_path = os.path.join(folder_path, file_name)
                table_dict['test_0'] = pd.read_csv(file_path)
    return table_dict
            
def calculate_similarity(result, target, rtol=1e-5, atol=1e-8):
        if result.empty or target.empty:
            return 0.0
        common_cols = list(set(result.columns) & set(target.columns))
        if not common_cols:
            return 0.0
        col_ratio = len(common_cols) / len(target.columns)
        
        result_common = result[common_cols].reset_index(drop=True)
        target_common = target[common_cols].reset_index(drop=True)
        sort_col = common_cols[0]
        result_sorted = result_common.sort_values(by=sort_col, key=lambda x: x.astype(str)).reset_index(drop=True)
        target_sorted = target_common.sort_values(by=sort_col, key=lambda x: x.astype(str)).reset_index(drop=True)
        min_len = min(len(result_sorted), len(target_sorted))
        result_sorted = result_sorted.iloc[:min_len].reset_index(drop=True)
        result_sorted = target_sorted.iloc[:min_len].reset_index(drop=True)
        col_ratio = col_ratio * min_len / max(len(result_sorted), len(target_sorted))
        try:
            assert_frame_equal(result_sorted, target_sorted, 
                             check_exact=False, 
                             rtol=rtol, atol=atol,
                             check_dtype=False)
            return col_ratio
        except AssertionError:
            numeric_cols = result_sorted.select_dtypes(include=[np.number]).columns.tolist()
            str_cols = result_sorted.select_dtypes(include=['object']).columns.tolist()
            numeric_mask = np.isclose(
                result_sorted[numeric_cols], 
                target_sorted[numeric_cols], 
                rtol=rtol, 
                atol=atol, 
                equal_nan=True
            )
            def compare_str_cols(a, b):
                return (a.isna() & b.isna()) | (a == b)
            
            str_mask = compare_str_cols(
                result_sorted[str_cols],
                target_sorted[str_cols]
            ).to_numpy()
            combined_mask = np.concatenate([numeric_mask, str_mask], axis=1)
            similarity = np.mean(combined_mask)
            return similarity

def calculate_column_similarity(result, target):
    """Calculate the proportion of correctly generated columns."""
    if result.empty or target.empty:
        return 0.0
    common_cols = list(set(result.columns) & set(target.columns))
    return len(common_cols) / len(target.columns)
        
def extract_last_variable(code_str):
    tree = ast.parse(code_str)
    last_var = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in reversed(node.targets):
                if isinstance(target, ast.Name):
                    last_var = target.id
                    break  
    return last_var  

def get_output_var(code_lines):
    if not code_lines:
        return None
    last_line = code_lines[-1]
    if '=' in last_line:
        var_part = last_line.split('=', 1)[0].strip()
        return var_part
    else:
        return None
def process_json_files(
    json_folder: str,
    folder_name: str,
    data_folder: str,
    output_base: str,
    length_type: int,
    start_num: int,
    end_num: int,
    llm_logs: List[Dict] = None,
    model_name: str = None,
    validation: str = "hard_match"
) -> Tuple[Dict, Dict]:
    global global_accuracy, global_column_similarity, case_results
    results = {}
    total_samples = 0
    correct_total = 0
    total_column_similarity = 0

    for num in range(start_num, end_num):
        
        if folder_name == "auto_pipeline":
            target_file = os.path.join(data_folder, f"length{length_type}_{num}", "target.csv")
            folder_path = os.path.join(data_folder, f"length{length_type}_{num}")
            output_path = os.path.join(output_base, f"length{length_type}","tables")
            json_file = f"length{length_type}_{num}.json"
            os.makedirs(output_path, exist_ok=True)
        elif folder_name == "buildings":
            target_file = os.path.join(data_folder, f"group{length_type}_{num}", f"target{length_type}_{num}.csv")
            folder_path = os.path.join(data_folder, f"group{length_type}_{num}")
            output_path = os.path.join(output_base, f"group{length_type}","tables")
            json_file = f"group{length_type}_{num}.json"
            os.makedirs(output_path, exist_ok=True)
        if not os.path.exists(target_file):
            continue
        json_path = os.path.join(json_folder, json_file)
        
        table_dict = read_csv_files(folder_path, folder_name)
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            total_samples += 1
            continue
        paths = data 
        
        path = paths[0]
        similarity = 0.0
        exec_env = {'pd': pd, **table_dict}
        try:
            code_str = None
            for code_line in path:
                code_str = code_line
                exec(code_str, exec_env)

            # Parse the full script once (not line-by-line) so a subscript
            # assignment on the last line (e.g. `target['col'] = ...`) doesn't
            # overwrite the real output variable name with None.
            last_var = extract_last_variable('\n'.join(path))
            result = exec_env.get(last_var, pd.DataFrame())
            if folder_name == "auto_pipeline":
                target = drop_leading_index_col_if_present(pd.read_csv(target_file))
            else:
                target = pd.read_csv(target_file)
            if validation == "autopipeline":
                avg_similarity, is_match, _, _ = compare_tables_matching(result, target)
                similarity = 1.0 if is_match else 0.0
                column_similarity = avg_similarity
            else:
                similarity = calculate_similarity(result, target)
                column_similarity = calculate_column_similarity(result, target)
        except Exception as e:
            column_similarity = 0
        total_column_similarity += column_similarity
        global_column_similarity["total_similarity"] += column_similarity
        global_column_similarity["total_samples"] += 1

        if similarity == 1.0:
            correct_total += 1
        total_samples += 1

        # Collect case-by-case results with cost/latency
        case_id = f"length{length_type}_{num}" if folder_name == "auto_pipeline" else f"group{length_type}_{num}"
        case_info = {
            "case_id": case_id,
            "length_type": length_type,
            "num": num,
            "accuracy": 1.0 if similarity == 1.0 else 0.0,
            "column_similarity": column_similarity,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "latency_seconds": 0.0,
            "estimated_cost": 0.0
        }

        # Match logs to this case by case_id from context var
        case_logs = [log for log in llm_logs if log.get("case_id") == case_id] if llm_logs else []

        # Calculate aggregated metrics from logs
        total_tokens = sum(log.get("tokens", {}).get("total", 0) for log in case_logs if log.get("tokens"))
        prompt_tokens = sum(log.get("tokens", {}).get("prompt", 0) for log in case_logs if log.get("tokens"))
        completion_tokens = sum(log.get("tokens", {}).get("completion", 0) for log in case_logs if log.get("tokens"))
        total_latency = sum(log.get("latency_seconds", 0) for log in case_logs)

        case_info["total_tokens"] = total_tokens
        case_info["prompt_tokens"] = prompt_tokens
        case_info["completion_tokens"] = completion_tokens
        case_info["latency_seconds"] = total_latency
        if model_name:
            case_info["estimated_cost"] = calculate_cost(prompt_tokens, completion_tokens, model_name)

        case_results.append(case_info)


    global_accuracy["total_samples"] += total_samples
    global_accuracy["correct_total"] += correct_total


    total_acc = correct_total / total_samples if total_samples else 0.0
    average_column_similarity = total_column_similarity / total_samples if total_samples else 0.0

    return {
        "accuracy": {
            "total_accuracy": total_acc,
            "total_samples": total_samples,
            "correct_total": correct_total,
            "average_column_similarity": average_column_similarity
        }
    }

def main(json_folder, data_folder, output_base, length_types, start_num, end_num, data_type=None, model_name=None, validation="hard_match"):
    global global_accuracy, case_results
    folder_name = data_type if data_type else os.path.basename(data_folder)
    if folder_name not in ["auto_pipeline", "buildings"]:
            raise ValueError(f"Unsupported folder name: {folder_name}")

    # Parse LLM logs. Single-length invocations (how run_length*.sh /
    # run_cases_iteratively.py always call this) read from the matching
    # per-length log file written by main.py's LLMClient(log_tag=...),
    # instead of the shared file every length otherwise races on.
    llm_logs = []
    if model_name:
        log_suffix = f"_length{length_types[0]}" if len(length_types) == 1 else ""
        log_file = f"logs/llm_queries_{model_name}{log_suffix}.jsonl"
        llm_logs = parse_llm_logs(log_file)

    for length_type in length_types:
        if folder_name == "auto_pipeline":
            json_dir = os.path.join(json_folder, f"length{length_type}")
            output_dir = os.path.join(output_base, f"length{length_type}")
        elif folder_name == "buildings":
            json_dir = os.path.join(json_folder, f"group{length_type}")
            output_dir = os.path.join(output_base, f"group{length_type}")
        os.makedirs(output_dir, exist_ok=True)
        

        result_data = process_json_files(
            json_folder=json_dir,
            folder_name=folder_name,
            data_folder=data_folder,
            output_base=output_base,
            length_type=length_type,
            start_num=start_num,
            end_num=end_num,
            llm_logs=llm_logs,
            model_name=model_name,
            validation=validation
        )
        

        detail_path = os.path.join(output_dir, 'detail.json')
        accuracy_path = os.path.join(output_dir, 'accuracy.json')
        
        # with open(detail_path, 'w') as f:
        #     json.dump(result_data["results"], f, indent=4)
            
        with open(accuracy_path, 'w') as f:
            json.dump(result_data["accuracy"], f, indent=4)
            print(f"Length Type {length_type} Accuracy: {result_data['accuracy']['total_accuracy']:.2f}")
            print(f"Length Type {length_type} Column Similarity: {result_data['accuracy']['average_column_similarity']:.2f}")  # 新增：打印Column Similarity

    # Output case-by-case summary to CSV
    if case_results:
        csv_path = os.path.join(output_base, 'case_by_case_summary.csv')
        df = pd.DataFrame(case_results)
        df = df[['case_id', 'length_type', 'num', 'accuracy', 'column_similarity', 'prompt_tokens', 'completion_tokens', 'total_tokens', 'latency_seconds', 'estimated_cost']]
        df.to_csv(csv_path, index=False)
        print(f"\nCase-by-case summary saved to {csv_path}")

    global_total_accuracy = (
        global_accuracy["correct_total"] / global_accuracy["total_samples"]
        if global_accuracy["total_samples"] else 0.0
    )
    global_total_column_similarity = (
        global_column_similarity["total_similarity"] / global_column_similarity["total_samples"]
        if global_column_similarity["total_samples"] else 0.0
    )
    with open(os.path.join(output_base, 'global_accuracy.json'), 'w') as f:
        json.dump(global_accuracy, f, indent=4)
    with open(os.path.join(output_base, 'global_column_similarity.json'), 'w') as f:
        json.dump(global_column_similarity, f, indent=4)
    print(f"Global Total Accuracy: {global_total_accuracy:.4f}")
    print(f"Global Total Column Similarity: {global_total_column_similarity:.4f}")  # 新增：打印全局列相似度

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_folder', type=str, default='./result/auto_pipeline')
    parser.add_argument('--data_folder', type=str, default='./data/auto_pipeline')
    parser.add_argument('--output_base', type=str, default='./predict/auto_pipeline')
    parser.add_argument('--length_types', type=int, nargs='+', default=[6])
    parser.add_argument('--start_num', type=int, default=0)
    parser.add_argument('--end_num', type=int, default=100)
    parser.add_argument('--data_type', type=str, default=None, help="Override data type (auto_pipeline or buildings). Defaults to basename of data_folder.")
    parser.add_argument('--model_name', type=str, default=None, help="Model name for cost calculation (e.g., gpt-4.1-mini). Used to find LLM logs.")
    parser.add_argument('--validation', type=str, choices=["hard_match", "autopipeline"], default="hard_match",
                         help="Validation strategy: 'hard_match' (default, evaluator's own similarity scoring) or "
                              "'autopipeline' (validation.hard_match.compare_tables_matching, same scoring used by "
                              "Langraph/mcts_search.py's --validation autopipeline).")
    args = parser.parse_args()
    main(
        json_folder=args.json_folder,
        data_folder=args.data_folder,
        output_base=args.output_base,
        length_types=args.length_types,
        start_num=args.start_num,
        end_num=args.end_num,
        data_type=args.data_type,
        model_name=args.model_name,
        validation=args.validation
    )