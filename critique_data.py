import traceback
import argparse
import json
import csv
import pdb
import shutil
import pandas as pd 
import multiprocessing

# from methods.precursor import precursor
from methods.multi_step import multi_step
from methods.single_step_cot import single_step_cot
from methods.critique import critique
from log_util.log_util import setup_logging, create_logger
from judges import judge
from llm.llm_models import LLMClient, TokenUsageTracker


def format_past_attempts(past_attempts):
    """Format a list of past failed attempt dicts into a context string for prompts."""
    if not past_attempts:
        return ""
    lines = ["--- Past Failed Attempt(s) from Previous Iteration(s) ---"]
    for attempt in past_attempts:
        lines.append(f"\n[Iteration {attempt['iteration']}] Score: {attempt['score']:.4f}, Succeeded: False")
        lines.append(f"Operations Tried: {attempt['operation_history']}")
        lines.append("Generated Code:")
        lines.append("```python")
        lines.append(attempt["code"])
        lines.append("```")
    lines.append("\n---")
    return "\n".join(lines)


def avg_tup(list_tup):
    if len(list_tup) == 0:
        return (0, 0, 0)
    avg_cost = 0
    avg_lat = 0
    for tup in list_tup:
        avg_cost += tup[2]
        avg_lat += tup[3]
    avg_cost = avg_cost / len(list_tup)
    avg_lat = avg_lat / len(list_tup)

    avg = (list_tup[0][0], avg_cost, avg_lat)
    return avg


def avg_tup_(list_tup):
    if len(list_tup) == 0:
        return (0, 0, 0)
    print("_________________________")
    print(f"averaging {list_tup}")
    avg_cost = 0
    avg_lat = 0
    avg_score = 0
    for tup in list_tup:
        avg_cost += tup[2]
        avg_lat += tup[3]
        avg_score += tup[1]
    avg_cost = avg_cost / len(list_tup)
    avg_lat = avg_lat / len(list_tup)
    avg_score = avg_score / len(list_tup)
    # here
    avg = (list_tup[0][1], avg_score, avg_cost, avg_lat)
    return avg


def ms(args, length, id, log_dir, experiment_name, past_context_str=""):
    results = []
    true_tup = []
    false_tup = []
    true_tup_ = []
    false_tup_ = []
    for i in range(0, args.no_of_runs):
        if args.single_step_cot:
            ms_info = single_step_cot(args, length, id, log_dir, experiment_name, i, past_context_str)
        else:
            ms_info = multi_step(args, length, id, log_dir, experiment_name, i, past_context_str)
        results.append(ms_info)

    for tup in results:
        multistep_path = f"{args.result_directory}/multi_step.csv"
        with open(multistep_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((f"{length}_{id}",) + tup)
        # Autologtuple((f"{length}_{id}",) + tup,
        #              sheet_dir["sheet_2"],
        #              worksheet_name=sheets["sm"],
        #              creds_file=creds_path
        #             )

        if tup[1] == True:
            true_tup_.append(tup)
            # print(f"{tup} in true tup")
        else:
            # print(f"{tup} in false tup")
            false_tup_.append(tup)

        if tup[0] == True:
            true_tup.append(tup)
            # print(f"{tup} in true tup")
        else:
            # print(f"{tup} in false tup")
            false_tup.append(tup)

    if len(true_tup_) >= args.majority_voting:
        print(f"avging {true_tup_}")
        avged_tup_ = avg_tup_(true_tup_)
    else:
        print(f"avging {false_tup_}")
        avged_tup_ = avg_tup_(false_tup_)

    if len(true_tup) >= args.majority_voting:
        avged_tup = avg_tup(true_tup)
    else:
        avged_tup = avg_tup(false_tup)
    # Return the operation_history of the last ms_info for now

    return avged_tup + avged_tup_, ms_info[-1]


def crit(args, length, id_, operation_history, past_context_str="", judge_reason=""):
    critique_path = f"{args.result_directory}/critique.csv"

    print("CRITIQUE FINAL RESULTS:")
    if "fd" in args.critique_setting:
        # The last flag corresponds to the few shot case.
        # 1 → we use few shot
        # 0 → we do not use few shot
        if args.few_shot:
            fd_flags = [1, 0, 0, 1]
        else:
            fd_flags = [1, 0, 0, 0]

        abl_a = critique(
            args, length, id_, args.log_directory, fd_flags, 0, operation_history,
            past_context_str=past_context_str, judge_reason=judge_reason
        )

        with open(critique_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((f"{length}_{id_}", "fd") + abl_a)

        if abl_a[0] == True:
            print("Success!")
            print(abl_a)
            return abl_a
        else:
            result = abl_a

    if "metadata" in args.critique_setting:
        # The last flag corresponds to the few shot case.
        # 1 → we use few shot
        # 0 → we do not use few shot
        if args.few_shot:
            metadata_flags = [1, 1, 0, 1]
        else:
            metadata_flags = [1, 1, 0, 0]

        abl_ab = critique(
            args, length, id_, args.log_directory, metadata_flags, 0, operation_history,
            past_context_str=past_context_str, judge_reason=judge_reason
        )
        # Add critique_type when logging
        with open(critique_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((f"{length}_{id_}", "metadata") + abl_ab)
        if abl_ab[0] == True:
            print("Success!")
            print(abl_ab)
            return abl_ab
        else:
            result = abl_ab

    if "annonymization" in args.critique_setting:
        # The last flag corresponds to the few shot case.
        # 1 → we use few shot
        # 0 → we do not use few shot
        if args.few_shot:
            anonymization_flags = [1, 1, 1, 1]
        else:
            anonymization_flags = [1, 1, 1, 0]
        abl_abc = critique(
            args,
            length,
            id_,
            args.log_directory,
            anonymization_flags,
            0,
            operation_history,
            past_context_str=past_context_str,
            judge_reason=judge_reason,
        )
        # Add critique_type when logging
        with open(critique_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((f"{length}_{id_}", "annonymization") + abl_abc)
        if abl_abc[0] == True:
            print("Success!")
        else:
            print("Failed!")
        print(abl_abc)
        return abl_abc

    print("Failed!")
    print(result)
    return result


def get_parser():
    parser = argparse.ArgumentParser(
        description="Critique Data Script Parameterization"
    )

    # Scalar integer parameters
    parser.add_argument("--len_id", type=int, default=5, help="Len ID")
    parser.add_argument("--max_len_id", type=int, default=5, help="Max Len ID")
    parser.add_argument("--target_id", type=int, default=12, help="Target ID")
    parser.add_argument("--max_target_id", type=int, default=40, help="Max Target ID")
    parser.add_argument("--target-per", type=int, default=25, help="Target Percentage")

    # Boolean flags
    parser.add_argument("--is-perc", action="store_true", help="Set is_perc to True")
    parser.add_argument(
        "--no-perc", dest="is_perc", action="store_false", help="Set is_perc to False"
    )
    parser.set_defaults(is_perc=False)
    
    #corresponds to table 9 from paper
    parser.add_argument(
        "--judge",
        type=str,
        default="gt",
        choices=["gt", "llm", "det_score", "llm_score", "llm_score_hybrid"],
        help="Judging technique for critique planning", 
    )

    parser.add_argument(
        "--hint-source",
        type=str,
        default="none",
        choices=["v1_kv", "v1_text", "v2", "v3"],
        help="Hint source selection",
    )
    parser.add_argument(
        "--anon-flag", action="store_true", help="Set anon_flag to True"
    )

    parser.add_argument(
        "--no-static-hints",
        dest="no_static_hints",
        action="store_true",
        default=False,
        help="Disable general purpose static hints in the prompt",
    )

    parser.add_argument(
        "--validation",
        type=str,
        default="hard_match",
        choices=["hard_match", "autopipeline"],
        help="Validation method: 'hard_match' uses compare_lists_matching (partial credit), 'autopipeline' uses compare_tables (binary match)",
    )

    parser.add_argument(
        "--no-anon",
        dest="anon_flag",
        action="store_false",
        help="Set anon_flag to False",
    )
    parser.set_defaults(anon_flag=False)

    # Computed lengths (override if desired)
    parser.add_argument(
        "--target-length",
        type=int,
        default=int(max(3, 10 * 0.31342417815924284)),
        help="Computed target length",
    )
    parser.add_argument(
        "--source-length",
        type=int,
        default=int(max(3, 10 * 0.9682615757193975)),
        help="Computed source length",
    )

    # Flow control flags
    parser.add_argument("--join-flag", type=int, default=0, help="Join flag")
    parser.add_argument("--aggregate-flag", type=int, default=0, help="Aggregate flag")
    parser.add_argument(
        "--fd-flag", type=int, default=0, help="Functional dependency flag"
    )

    # Lists of floats
    parser.add_argument(
        "--join-hints-truncate",
        type=float,
        nargs="+",
        # 0 : high threshold for distinct value ratio from at least one of the columns
        # 1 : high threshold for jaccard similarity
        # 2 : high threshold for jaccard containment
        # 3 : high threshold for value-overlap in case of numerical columns
        # 4 : high leftness
        # 5 : high sortedness
        default=[0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
        help="Join hints truncate thresholds",
    )
    parser.add_argument(
        "--aggregate-hints-truncate",
        type=float,
        nargs="+",
        # aht = [
        # dvr_ub, dvr_lb,
        # leftness_ub, leftness_lb,
        # emptiness_ub, emptiness_lb,
        # peak_frequency_ub, peak_frequency_lb,
        # value_range_ub, value_range_lb
        # ]
        default=[0.8, 0.2, 0.8, 0.2, 0.8, 0.2, 0.8, 0.2, 0.8, 0.2],
        help="Aggregate hints truncate thresholds",
    )

    parser.add_argument(
        "--critique_setting",
        type=str,
        nargs="+",
        default=["fd", "metadata"],
        help="Critique settings (e.g., fd, metadata, annonymization). You can add more by separating with space",
    )
    parser.add_argument(
        "--critique_type",
        type=str,
        default="history",
        choices=["hard", "soft", "history"],
        help="Type of critique to perform, the actual effect is to load prompt file from prompts/{critique_type}_critique.txt",
    )

    # Other parameters
    parser.add_argument("--token-limit", type=int, default=120000, help="Token limit")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model name")
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs-auto-suggest-llm-21-04",
        help="Log directory",
    )
    parser.add_argument(
        "--experiment-name", type=str, default="feature_v3_2", help="Experiment name"
    )
    parser.add_argument("--no_of_runs", type=int, default=1, help="Number of runs")
    parser.add_argument(
        "--cases",
        type=str,
        nargs="+",
        default=None,
        help="Explicit list of case IDs to run, e.g. --cases 1_41 4_18 9_70. "
             "Overrides --len_id / --target_id / --max_target_id.",
    )

    # Complex dict via JSON
    default_hints = {
        "t1": 0.7,
        "t2": 0.7,
        "t3": 0.7,
        "t4": 10,
        "t5": 0.1,
        "t6": 0.8,
        "t7": 0.4,
        "t8": 0.3,
        "t9": 0.2,
        "t10": 0.3,
        "t11": 0.5,
        "t12": 0.7,
        "t13": 0.2,
    }
    parser.add_argument(
        "--hints-v3-truncates",
        type=json.loads,
        default=default_hints,
        help="JSON string for hints_v3_truncates dict",
    )

    parser.add_argument(
        "--rag_db_uri",
        type=str,
        default="rag_pipeline/test_dummy/milvus_demo_4.db",
        help="URI for the RAG DB.",
    )

    parser.add_argument(
        "--rag_embedding_model",
        type=str,
        default="Qwen/Qwen3-Embedding-0.6B",
        help="Embedding model for the RAG DB.",
    )

    parser.add_argument(
        "--rag_embedding_dim",
        type=int,
        default=8192,
        help="Max dimension size of the embedding model for the RAG DB.",
    )

    parser.add_argument(
        "--rag_db_collection",
        type=str,
        default="plan_docs",
        help="RAG DB collection that contains all the documents.",
    )

    parser.add_argument(
        "--rag_topk",
        type=int,
        default=3,
        help="Top-k relevant samples to be retrieved from the RAG DB.",
    )

    parser.add_argument(
        "--rag_embedding_batch_size",
        type=int,
        default=2,
        help="Batch size for the embedding model in the RAG DB.",
    )

    parser.add_argument(
        "--rag_output_fields",
        type=str,
        default="doc",
        help="A comma separated string containing all the fields required to be retrieved from the RAG DB.",
    )

    parser.add_argument(
        "--rag_retrieval_strategy",
        type=str,
        choices=["text", "feature"],
        default="text",
        help="Retrieval strategy: 'text' (embed query, search text collection) or 'feature' (compute 23-dim, search feature collection).",
    )

    parser.add_argument(
        "--rag_feature_collection",
        type=str,
        default="plan_docs_features",
        help="Milvus collection name for feature vectors (used when rag_retrieval_strategy=feature).",
    )

    parser.add_argument(
        "--feature_norm_stats_path",
        type=str,
        default=None,
        help="Path to feature_norm_stats.json for z-score normalization (used when rag_retrieval_strategy=feature). "
             "Defaults to rag_pipeline/feature_norm_stats.json."
    )

    parser.add_argument(
        "--intermediate_materialization",
        action="store_true",
        help="Materialize intermediate results",
    )

    parser.add_argument(
        "--few_shot",
        action="store_true",
        help="Add Few Shot Examples",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="github",
        choices=["github", "monteprep"],
        help="Benchmark dataset: 'github' or 'monteprep'.",
    )
    parser.add_argument(
        "--single_step_cot",
        action="store_true",
        help="Use Single Step CoT instead of Multi Step",
    )

    parser.add_argument(
        "--iterative",
        type=int,
        default=1,
        help="Number of full ms+critique iterations per case. In iterations >=2, past "
             "operation history, code, and score are injected into prompts.",
    )

    # parser.add_argument(
    #     "--combine_ask_and_configure",
    #     action="store_true",
    #     help="Allow combining ask and configure into one step",
    # )

    # parser.add_argument(
    #     "--no_thinking",
    #     action="store_true",
    #     help="Disable thinking process when asked for next operator",
    # )

    return parser


_CASE_TIMEOUT = 600  # 10 minutes per case


def _critique_case_worker(args, length, case, result_queue):
    """Runs one SSCoT/multistep+critique case fully in a child process."""
    try:
        case_path = f"{length}_{case}"
        main_folder_base = (
            "autopipeline-benchmarks/monteprep-pipelines"
            if getattr(args, "benchmark", "github") == "monteprep"
            else "autopipeline-benchmarks/github-pipelines"
        )
        code_path = f"{main_folder_base}/length{case_path}/python_recovered.py"
        num_iterations = getattr(args, "iterative", 1)
        past_attempts = []
        succeeded = False

        # Create llm_client here (subprocess cannot share the parent's client)
        _token_tracker = TokenUsageTracker()
        _case_logger = create_logger("JUDGE", args.log_directory, length, case, case)
        _llm_client = LLMClient(model=args.model, tracker=_token_tracker, logger=_case_logger)

        for iter_num in range(1, num_iterations + 1):
            past_context_str = format_past_attempts(past_attempts)

            ms_info, operation_history = ms(
                args, length, case, args.log_directory, args.experiment_name, past_context_str
            )
            result = (case_path,) + ms_info

            average_multistep_path = f"{args.result_directory}/average_multi_step.csv"
            with open(average_multistep_path, "a", newline="") as f:
                csv.writer(f).writerow(result)

            # Read generated code and save a per-iteration copy for reproducibility
            code = ""
            try:
                with open(code_path) as f:
                    code = f.read()
            except Exception:
                pass
            if code:
                shutil.copy2(code_path, f"{main_folder_base}/length{case_path}/python_recovered_iter_{iter_num}.py")

            # Determine whether to enact critique using the configured judge
            judge_reason = ""
            enact_critique = not result[1]
            if args.judge != "gt":
                df_generated_path = f"{main_folder_base}/length{case_path}/target_multisource.csv"
                df_ground_truth_path = f"{main_folder_base}/length{case_path}/target.csv"
                try:
                    df_generated = pd.read_csv(df_generated_path, low_memory=False)
                    df_ground_truth = pd.read_csv(df_ground_truth_path, low_memory=False)
                    df_ground_truth.drop(columns=df_ground_truth.columns[0], axis=1, inplace=True)
                    is_correct, judge_reason = judge(df_generated, df_ground_truth, args.judge, _llm_client, logger=_case_logger)
                    enact_critique = not is_correct
                except Exception as e:
                    print(f"Judge failed for {case_path}, falling back to gt: {e}")
                    enact_critique = not result[1]

            if not enact_critique:  # output judged as correct
                shutil.copy2(code_path, f"{main_folder_base}/length{case_path}/python_recovered_successful.py")
                print("Success!")
                succeeded = True
                break

            # No critique for single-step CoT
            if args.single_step_cot:
                break

            crit_info = crit(args, length, case, operation_history, past_context_str, judge_reason=judge_reason)

            average_crit_path = f"{args.result_directory}/final_critique.csv"
            with open(average_crit_path, "a", newline="") as f:
                csv.writer(f).writerow(crit_info)

            if crit_info[0]:  # critique succeeded
                shutil.copy2(code_path, f"{main_folder_base}/length{case_path}/python_recovered_successful.py")
                print("Success!")
                succeeded = True
                break

            # Accumulate past attempt context for the next iteration (if any remain)
            if iter_num < num_iterations:
                # ms_info tuple: (is_correct, avg_cost, avg_lat, …, avg_score)
                # avg_score sits at index 6 (avged_tup_[3])
                score = ms_info[6] if len(ms_info) > 6 else 0.0
                past_attempts.append({
                    "iteration": iter_num,
                    "operation_history": str(operation_history),
                    "code": code,
                    "score": score,
                })

        if not succeeded:
            print("Failed!")

        result_queue.put(("ok", None))
    except Exception:
        result_queue.put(("error", traceback.format_exc()))


if __name__ == "__main__":

    args = get_parser().parse_args()
    args.static_hints = not args.no_static_hints
    args.majority_voting = args.no_of_runs // 2 + 1

    # set up logging
    print(args)
    experiment_log_directory, log_directory, results_directory = setup_logging(
        args, args.log_dir, args.experiment_name
    )
    args.log_directory = log_directory
    args.result_directory = results_directory

    # Build case list: --cases overrides --len_id / --target_id / --max_target_id
    if args.cases:
        # Each entry is "length_id", e.g. "1_41"
        case_pairs = [(int(c.split("_")[0]), int(c.split("_")[1])) for c in args.cases]
    else:
        length = args.len_id
        case_pairs = [(length, cid) for cid in range(args.target_id, args.max_target_id)]

    processed_without_exceptions = 0

    for length, case in case_pairs:

        print("Processing:", case)

        case_path = f"{length}_{case}"

        _result_queue = multiprocessing.Queue()
        _proc = multiprocessing.Process(
            target=_critique_case_worker,
            args=(args, length, case, _result_queue),
            daemon=True,
        )
        _proc.start()
        _proc.join(timeout=_CASE_TIMEOUT)

        if _proc.is_alive():
            print(f"[TIMEOUT] Case {case_path} exceeded {_CASE_TIMEOUT}s — killing process")
            _proc.terminate()
            _proc.join()
        elif not _result_queue.empty():
            _status, _payload = _result_queue.get()
            if _status == "ok":
                processed_without_exceptions += 1
            else:
                print(f"Error processing case {case_path}:\n{_payload}")
        else:
            print(f"Case {case_path} exited without result")

    print(processed_without_exceptions)
