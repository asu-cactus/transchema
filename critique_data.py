import traceback
import argparse
import json
import csv
import pdb

# from methods.precursor import precursor
from methods.multi_step import multi_step
from methods.single_step_cot import single_step_cot
from methods.critique import critique
from log_util.log_util import setup_logging


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


def ms(args, length, id, log_dir, experiment_name):
    results = []
    true_tup = []
    false_tup = []
    true_tup_ = []
    false_tup_ = []
    for i in range(0, args.no_of_runs):
        if args.single_step_cot:
            ms_info = single_step_cot(args, length, id, log_dir, experiment_name, i)
        else:
            ms_info = multi_step(args, length, id, log_dir, experiment_name, i)
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


def crit(args, length, id_, operation_history):
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
            args, length, id_, args.log_directory, 
            fd_flags, 0, operation_history
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
            args, length, id_, args.log_directory, 
            metadata_flags, 0, operation_history
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
            args, length, id_, args.log_directory, 
            anonymization_flags, 0, operation_history
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
        default=[
            0.027387593197926163,
            0.8763891522960383,
            0.6923226156693141,
            0.8946066635038473,
            0.14038693859523377,
            0.8007445686755367,
        ],
        help="Join hints truncate thresholds",
    )
    parser.add_argument(
        "--aggregate-hints-truncate",
        type=float,
        nargs="+",
        default=[0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1],
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
        help="URI for the RAG DB."
    )

    parser.add_argument(
        "--rag_embedding_model",
        type=str,
        default="Qwen/Qwen3-Embedding-0.6B",
        help="Embedding model for the RAG DB."
    )

    parser.add_argument(
        "--rag_embedding_dim",
        type=int,
        default=8192,
        help="Max dimension size of the embedding model for the RAG DB."
    )

    parser.add_argument(
        "--rag_db_collection",
        type=str,
        default="plan_docs",
        help="RAG DB collection that contains all the documents."
    )

    parser.add_argument(
        "--rag_topk",
        type=int,
        default=3,
        help="Top-k relevant samples to be retrieved from the RAG DB."
    )

    parser.add_argument(
        "--rag_embedding_batch_size",
        type=int,
        default=2,
        help="Batch size for the embedding model in the RAG DB."
    )

    parser.add_argument(
        "--rag_output_fields",
        type=str,
        default="doc",
        help="A comma separated string containing all the fields required to be retrieved from the RAG DB."
    )

    parser.add_argument(
        "--rag_retrieval_strategy",
        type=str,
        choices=["text", "feature"],
        default="text",
        help="Retrieval strategy: 'text' (embed query, search text collection) or 'feature' (compute 23-dim, search feature collection)."
    )

    parser.add_argument(
        "--rag_feature_collection",
        type=str,
        default="plan_docs_features",
        help="Milvus collection name for feature vectors (used when rag_retrieval_strategy=feature)."
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
        "--single_step_cot",
        action="store_true",
        help="Use Single Step CoT instead of Multi Step",
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


if __name__ == "__main__":

    args = get_parser().parse_args()
    args.majority_voting = args.no_of_runs // 2 + 1

    # set up logging
    print(args)
    experiment_log_directory, log_directory, results_directory = setup_logging(
        args, args.log_dir, args.experiment_name
    )
    args.log_directory = log_directory
    args.result_directory = results_directory
    # sys.exit()

    length = args.len_id
    start = args.target_id
    end = args.max_target_id

    cases = list(range(start, end))

    processed_without_exceptions = 0

    for case in cases:

        print("Processing:", case)

        case_path = f"{length}_{case}"
        # log_dir = f"crit_logs/{case_path}"

        try:
            # compute multisource
            ms_info, operation_history = ms(
                args, length, case, args.log_directory, args.experiment_name
            )

            # Format as a single row with consistent columns
            # print(f"case_path: {case_path} + ms_info: {ms_info}")
            result = (case_path,) + ms_info

            # Fill the average result sheets
            average_multistep_path = f"{args.result_directory}/average_multi_step.csv"
            with open(average_multistep_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(result)

            if not result[1]:
                if args.single_step_cot:
                    # No critique for single step cot
                    continue

                # critique iff ms is wrong

                crit_info = crit(args, length, case, operation_history)
                average_crit_path = f"{args.result_directory}/final_critique.csv"
                with open(average_crit_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(crit_info)

            else:
                print("Success!")

            processed_without_exceptions += 1

        except Exception as e:
            print("".join(traceback.format_exc()))
            print(f"Error processing case {case_path}: {str(e)}")

    print(processed_without_exceptions)
