import traceback
import argparse
import json
import csv
import pdb

from methods.precursor import precursor
from methods.critique import critique

from log_util.log_util import setup_logging


def avg_tup(list_tup):
    avg_cost = 0
    avg_lat = 0
    for tup in list_tup:
        avg_cost += tup[3]
        avg_lat += tup[4]
    avg_cost = avg_cost / len(list_tup)
    avg_lat = avg_lat / len(list_tup)

    avg = (list_tup[0][0], avg_cost, avg_lat)
    return avg


def avg_tup_(list_tup):
    print("_________________________")
    print(f"averaging {list_tup}")
    avg_cost = 0
    avg_lat = 0
    avg_score = 0
    for tup in list_tup:
        avg_cost += tup[3]
        avg_lat += tup[4]
        avg_score += tup[2]
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
        try:
            ms_info = precursor(args, length, id, log_dir, experiment_name, i)
        except Exception as e:
            print("".join(traceback.format_exc()))
            ms_info = ("precursor error " + str(e),)
        # print(ms_info)
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

    return (avged_tup + avged_tup_,), ms_info[-1]


def crit(args, length, id_, operation_history):
    a_results = []
    ab_results = []
    abc_results = []

    # for strict match
    a_true = []
    a_false = []
    ab_true = []
    ab_false = []
    abc_true = []
    abc_false = []

    # for soft match
    a_true_ = []
    a_false_ = []
    ab_true_ = []
    ab_false_ = []
    abc_true_ = []
    abc_false_ = []

    avg_results = []
    critique_path = f"{args.result_directory}/critique.csv"

    for i in range(0, args.no_of_runs):
        if "fd" in args.critique_setting:
            abl_a = critique(
                args, length, id_, args.log_directory, [1, 0, 0], 0, operation_history
            )
            a_results.append(abl_a)
            for tup in a_results:
                # Add critique_type when logging
                # Autologtuple((f"{length}_{id_}", "fd") + tup,
                #             sheet_dir["sheet_2"],
                #             worksheet_name=sheets["sc"],
                #             creds_file=creds_path
                #             )
                with open(critique_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow((f"{length}_{id_}", "fd") + tup)
                if tup[1] == True:
                    a_true_.append(tup)
                else:
                    a_false_.append(tup)
                if tup[0] == True:
                    a_true.append(tup)
                else:
                    a_false.append(tup)
                if len(a_true) >= args.majority_voting:
                    avg_a = avg_tup(a_true)
                else:
                    avg_a = avg_tup(a_false)
                if len(a_true_) >= args.majority_voting:
                    avg_a_ = avg_tup_(a_true_)
                else:
                    avg_a_ = avg_tup_(a_false_)
            avg_results.append(("fd",) + avg_a + avg_a_)

        if "metadata" in args.critique_setting:
            abl_ab = critique(
                args, length, id_, args.log_directory, [1, 1, 0], 0, operation_history
            )
            ab_results.append(abl_ab)
            for tup in ab_results:
                # Add critique_type when logging
                with open(critique_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow((f"{length}_{id_}", "metadata") + tup)
                if tup[1] == True:
                    ab_true_.append(tup)
                else:
                    ab_false_.append(tup)
                if tup[0] == True:
                    ab_true.append(tup)
                else:
                    ab_false.append(tup)
                if len(ab_true) >= args.majority_voting:
                    avg_ab = avg_tup(ab_true)
                else:
                    avg_ab = avg_tup(ab_false)
                if len(ab_true_) >= args.majority_voting:
                    avg_ab_ = avg_tup_(ab_true_)
                else:
                    avg_ab_ = avg_tup_(ab_false_)
            avg_results.append(("metadata",) + avg_ab + avg_ab_)

        if "annonymization" in args.critique_setting:
            abl_abc = critique(
                args, length, id_, args.log_directory, [1, 1, 1], 0, operation_history
            )
            abc_results.append(abl_abc)
            for tup in abc_results:
                # Add critique_type when logging
                with open(critique_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow((f"{length}_{id_}", "annonymization") + tup)
                if tup[1] == True:
                    abc_true_.append(tup)
                else:
                    abc_false_.append(tup)
                if tup[0] == True:
                    abc_true.append(tup)
                else:
                    abc_false.append(tup)
                if len(abc_true) >= args.majority_voting:
                    avg_abc = avg_tup(abc_true)
                else:
                    avg_abc = avg_tup(abc_false)
                if len(abc_true_) >= args.majority_voting:
                    avg_abc_ = avg_tup_(abc_true_)
                else:
                    avg_abc_ = avg_tup_(abc_false_)
            avg_results.append(("annonymization",) + avg_abc + avg_abc_)

    print("CRITIQUE FINAL RESULTS:")
    print(avg_results)
    print("=" * 30)

    max_val = -1
    max_ind = 0

    for i, result in enumerate(avg_results):
        if result[4] > max_val:  # index 4 because critique_type is at 0
            max_val = result[4]
            max_ind = i

    # Add 'MAX' marker while preserving critique_type
    avg_results[max_ind] = avg_results[max_ind][: len(avg_results[max_ind]) - 1] + (
        "MAX",
    )

    return avg_results


def get_parser():
    parser = argparse.ArgumentParser(
        description="Critique Data Script Parameterization"
    )

    # Scalar integer parameters
    parser.add_argument("--len_id", type=int, default=5, help="Len ID")
    parser.add_argument("--max_len_id", type=int, default=5, help="Max Len ID")
    parser.add_argument("--target_id", type=int, default=12, help="Target ID")
    parser.add_argument("--max-target_id", type=int, default=40, help="Max Target ID")
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
        default="v3",
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
        default=["fd"],
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
    parser.add_argument("--model", type=str, default="gpt-4.1-mini", help="Model name")
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs-auto-suggest-llm-21-04",
        help="Log directory",
    )
    parser.add_argument(
        "--experiment-name", type=str, default="feature_v3_2", help="Experiment name"
    )
    parser.add_argument("--no-of-runs", type=int, default=1, help="Number of runs")

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
        "--intermediate_materialization_flag",
        type=int,
        default=0,
        help="Intermediate materialization flag",
    )

    parser.add_argument(
        "--use_old_prompt", type=int, default=0, help="Use old prompt flag (0 or 1)"
    )
    parser.add_argument(
        "--combine_ask_and_configure",
        type=int,
        default=0,
        help="Combine ask and configure flag (0 or 1)",
    )
    parser.add_argument(
        "--no_thinking", type=int, default=0, help="No think flag (0 or 1)"
    )

    return parser


def main():

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
    end = args.max_target_id + 1
    # Autologtuple(("Start", "Test:", f"{length}_{start}",f"{length}_{end}",),sheet_dir["sheet_1"],
    #             creds_file=creds_path )

    cases = list(range(start, end))

    for case in cases:

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

            # critique iff ms is wrong
            # critique not supported yet for intermediate materialization
            if not result[1]:

                crit_info = crit(args, length, case, operation_history)
                average_crit_path = f"{args.result_directory}/average_critique.csv"
                for crit_ in crit_info:
                    crit_res = (case_path,) + crit_
                    with open(average_crit_path, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(crit_res)

        except Exception as e:
            print("".join(traceback.format_exc()))
            print(f"Error processing case {case_path}: {str(e)}")


if __name__ == "__main__":
    # Let's make it parameterized

    main()
