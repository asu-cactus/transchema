import os
import signal
import traceback
import argparse
import json
import csv
import glob
import pdb
import shutil
import time
import pandas as pd
import multiprocessing

# from methods.precursor import precursor
from methods.multi_step import multi_step
from methods.single_step_cot import single_step_cot
from methods.critique import critique
from log_util.log_util import setup_logging, create_logger
from judges import judge, build_nl_score_interpretation
from eval_score.cot_score import cot_value_based_score
from validation.fuzzy_match import compare_tables_fuzzy
from llm.llm_models import LLMClient, TokenUsageTracker, CostBudgetExceeded
from util.utils import resolve_main_folder, resolve_case_json, BENCHMARK_CHOICES, drop_leading_index_col_if_present


def _compute_attempt_context(generated_path, gt_path, n_samples, precomputed=None,
                             reward_mode="score", length=None, confidence=None):
    """Return (nl_score, generated_samples, score, timing_dict) for a given attempt.

    If precomputed=(df_gen, fd_f1, col_ratio, true_combined_score, debug_dict) is
    provided, the CSV and relative_csv_score are not re-run — avoiding duplicate
    get_column_map calls when the caller already has these values.

    reward_mode determines which score to return:
    - "score" (default): returns true_combined_score
    - "partial": returns fuzzy column-match ratio (matched_cols / total_target_cols) via compare_tables_fuzzy

    Returns timing_dict with keys: 'csv_load_ms', 'relative_score_ms', 'fuzzy_match_ms', 'total_ms'
    """
    nl_score = ""
    generated_samples = ""
    score = 0.0
    timing = {'csv_load_ms': 0, 'relative_score_ms': 0, 'fuzzy_match_ms': 0, 'total_ms': 0}
    context_start = time.time()

    try:
        if precomputed is not None:
            df_gen, fd_f1, col_ratio, true_combined_score, debug_dict = precomputed
        else:
            t0 = time.time()
            df_gen = pd.read_csv(generated_path, low_memory=False)
            df_gt = pd.read_csv(gt_path, low_memory=False)
            drop_leading_index_col_if_present(df_gt)
            timing['csv_load_ms'] = (time.time() - t0) * 1000

            t0 = time.time()
            _, col_ratio, _, fd_f1, true_combined_score, debug_dict = \
                cot_value_based_score(df_gen, df_gt, length=length, confidence=confidence)
            timing['relative_score_ms'] = (time.time() - t0) * 1000

        nl_score = build_nl_score_interpretation(fd_f1, col_ratio, true_combined_score, debug_dict)

        if df_gen is not None and len(df_gen) > 0:
            sample = df_gen.sample(n=min(n_samples, len(df_gen)), replace=False)
            generated_samples = (
                f"Schema: {list(df_gen.columns)}\n"
                f"Number of Tuples: {len(df_gen)}\n"
                f"Examples:\n{sample.to_string(index=False)}"
            )

        # Compute score based on reward_mode
        if reward_mode == "partial":
            # Load df_gt if not already loaded (for precomputed case)
            if precomputed is not None:
                t0 = time.time()
                df_gt = pd.read_csv(gt_path, low_memory=False)
                drop_leading_index_col_if_present(df_gt)
                timing['csv_load_ms'] = (time.time() - t0) * 1000

            # Use fuzzy column-match ratio: matched_cols / total_target_cols
            t0 = time.time()
            score, _ = compare_tables_fuzzy(df_gen, df_gt)
            timing['fuzzy_match_ms'] = (time.time() - t0) * 1000
        else:
            score = true_combined_score
    except Exception:
        # Previously a bare `pass`, which is how a two-month-old scoring regression
        # stayed invisible: every failure looked like a legitimate score of 0.0.
        print(f"[attempt-context] failed for {generated_path}, leaving score=0:\n"
              f"{traceback.format_exc()}")

    timing['total_ms'] = (time.time() - context_start) * 1000
    return nl_score, generated_samples, score, timing


def format_past_attempts(past_attempts):
    """Format a list of past attempt dicts into a context string for prompts.

    Each attempt may carry a "label" describing which attempt it is ("best scoring
    attempt", "most recent attempt", ...). ReAct-CoT passes two blocks per critique
    round -- the best-scoring attempt and the most recent one -- so the label cannot be
    hardcoded to "best scoring attempt" the way it used to be: one of the two is not the
    best, and mislabelling it tells the model the opposite of the truth.
    """
    if not past_attempts:
        return ""
    lines = ["--- Past Attempt(s) from Previous Iteration(s) ---"]
    for attempt in past_attempts:
        label = attempt.get("label", "best scoring attempt")
        # Existing callers pass an int iteration number; ReAct-CoT passes a descriptive
        # string ("Best so far", "Most recent"). Keep the old rendering for ints.
        it = attempt["iteration"]
        heading = f"Iteration {it}" if isinstance(it, int) else str(it)
        lines.append(f"\n[{heading}] Score: {attempt['score']:.4f}")
        lines.append(f"Operations Tried: {attempt['operation_history']}")
        if attempt.get("generated_samples"):
            lines.append(f"Generated Data ({label}):")
            lines.append(attempt["generated_samples"])
        if attempt.get("nl_score"):
            lines.append("Score Analysis:")
            lines.append(attempt["nl_score"])
        lines.append(f"Generated Code ({label}):")
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
    total_latency = 0  # SUM of latencies (not averaged) - actual time spent
    avg_score = 0     # AVERAGE of scores
    total_cost = 0    # SUM of costs (not averaged) - actual cost spent
    for tup in list_tup:
        total_latency += tup[2]     # tup[2] = time_elapsed - SUM these!
        avg_score += tup[3]         # tup[3] = score
        total_cost += tup[1]        # tup[1] = total_cost - SUM these!
    # KEEP BOTH cost and latency as SUMS (no division!)
    # These should represent actual total time and cost spent per iteration
    avg_score = avg_score / len(list_tup)     # Only average the score
    # Return: (first_cost, total_cost, total_latency, avg_score)
    avg = (list_tup[0][1], total_cost, total_latency, avg_score)
    return avg


def ms(args, length, id, log_dir, experiment_name, past_context_str="", token_tracker=None, budget=None):
    results = []
    true_tup = []
    false_tup = []
    true_tup_ = []
    false_tup_ = []
    ms_extras = None
    for i in range(0, args.no_of_runs):
        if args.single_step_cot:
            ms_info, ms_extras = single_step_cot(args, length, id, log_dir, experiment_name, i, past_context_str, token_tracker=token_tracker, budget=budget)
        else:
            ms_info, ms_extras = multi_step(args, length, id, log_dir, experiment_name, i, past_context_str, token_tracker=token_tracker, budget=budget)
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

    return avged_tup + avged_tup_, ms_info[-1], ms_extras


def crit(args, length, id_, operation_history, past_context_str="", judge_reason="", budget=None):
    critique_path = f"{args.result_directory}/critique.csv"

    benchmark = getattr(args, "benchmark", "github")
    main_folder = resolve_main_folder(benchmark)
    code_path = f"{main_folder}/length{length}_{id_}/python_recovered.py"

    attempts = []  # list of {"code": ..., "score": ..., "type": ...}

    generated_path = f"{main_folder}/length{length}_{id_}/target_multisource.csv"
    gt_path = f"{main_folder}/length{length}_{id_}/target.csv"

    def _snapshot(crit_type, crit_result, extras, reward_mode="score"):
        code = ""
        try:
            with open(code_path) as f:
                code = f.read()
        except Exception:
            pass
        nl_score, generated_samples, reward_score, score_timing = _compute_attempt_context(
            generated_path, gt_path, args.target_length, precomputed=extras,
            reward_mode=reward_mode, length=length
        )
        generated_csv_head = ""
        if extras is not None:
            try:
                df_gen = extras[0]
                if df_gen is not None and len(df_gen) > 0:
                    generated_csv_head = df_gen.head(10).to_csv(index=False)
            except Exception:
                pass
        attempts.append({
            "type": crit_type,
            "is_correct": crit_result[0],
            "score": reward_score,
            "cost": crit_result[1],
            "latency": crit_result[2],
            "nl_score": nl_score,
            "generated_samples": generated_samples,
            "code": code,
            "generated_csv_head": generated_csv_head,
            "score_calculation_time_ms": score_timing,
        })

    print("CRITIQUE FINAL RESULTS:")
    reward_mode = getattr(args, "reward", "score")

    # For mcts_style, run only one unified critique (fd variant) to match MCTS behavior
    if args.critique_type == "mcts_style":
        if args.few_shot:
            fd_flags = [1, 0, 0, 1]
        else:
            fd_flags = [1, 0, 0, 0]

        abl_a, a_extras = critique(
            args, length, id_, args.log_directory, fd_flags, 0, operation_history,
            past_context_str=past_context_str, judge_reason=judge_reason, budget=budget
        )

        with open(critique_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((f"{length}_{id_}", "mcts_style") + abl_a)

        _snapshot("mcts_style", abl_a, a_extras, reward_mode=reward_mode)
        print("Success!" if abl_a[0] else "Failed!")
        print(abl_a)
        return abl_a, attempts

    # Original multi-variant behavior for other critique types
    if "fd" in args.critique_setting:
        # The last flag corresponds to the few shot case.
        # 1 → we use few shot
        # 0 → we do not use few shot
        if args.few_shot:
            fd_flags = [1, 0, 0, 1]
        else:
            fd_flags = [1, 0, 0, 0]

        abl_a, a_extras = critique(
            args, length, id_, args.log_directory, fd_flags, 0, operation_history,
            past_context_str=past_context_str, judge_reason=judge_reason, budget=budget
        )

        with open(critique_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((f"{length}_{id_}", "fd") + abl_a)

        _snapshot("fd", abl_a, a_extras, reward_mode=reward_mode)
        if abl_a[0] == True:
            print("Success!")
            print(abl_a)
            return abl_a, attempts
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

        abl_ab, ab_extras = critique(
            args, length, id_, args.log_directory, metadata_flags, 0, operation_history,
            past_context_str=past_context_str, judge_reason=judge_reason, budget=budget
        )
        # Add critique_type when logging
        with open(critique_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((f"{length}_{id_}", "metadata") + abl_ab)
        _snapshot("metadata", abl_ab, ab_extras, reward_mode=reward_mode)
        if abl_ab[0] == True:
            print("Success!")
            print(abl_ab)
            return abl_ab, attempts
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
        abl_abc, abc_extras = critique(
            args,
            length,
            id_,
            args.log_directory,
            anonymization_flags,
            0,
            operation_history,
            past_context_str=past_context_str,
            judge_reason=judge_reason,
            budget=budget,
        )
        # Add critique_type when logging
        with open(critique_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow((f"{length}_{id_}", "annonymization") + abl_abc)
        _snapshot("anonymization", abl_abc, abc_extras, reward_mode=reward_mode)
        if abl_abc[0] == True:
            print("Success!")
        else:
            print("Failed!")
        print(abl_abc)
        return abl_abc, attempts

    print("Failed!")
    print(result)
    return result, attempts


def _critique_result_path(args, main_folder_base, case_path):
    """The CSV that critique reads as 'the resulting table' for this mode.

    Mirrors methods/critique.py::get_result_path, which is fixed per mode rather than
    per round -- so ReAct-CoT has to overwrite it between rounds (see
    _run_critique_rounds) or every round would critique the ORIGINAL generation output.
    """
    base = f"{main_folder_base}/length{case_path}"
    if getattr(args, "intermediate_materialization", False):
        return None  # materialization picks the newest intermediate itself; leave it alone
    if getattr(args, "single_step_cot", False):
        return f"{base}/target_multisource_cot.csv"
    return f"{base}/target_multisource.csv"


def _run_critique_rounds(args, length, case, main_folder_base, case_path,
                         operation_history, past_context_str, judge_reason, budget,
                         ms_score, ms_code, ms_nl_score, ms_generated_samples,
                         on_round=None):
    """Run up to --critique-rounds critique rounds over a single generation.

    Round 1 is exactly the existing single critique call, so --critique-rounds 1 (the
    default) is a no-op relative to previous behaviour.

    From round 2 on, each round is given the best-scoring attempt so far AND the most
    recent one via $PAST_ITERATION_CONTEXT$ (the critique prompt never receives code any
    other way -- it works from $OPERATIONS$ plus the result table). The best attempt's
    output CSV is also staged over the path critique reads, so $RES_SCHEMA$/$RES_EXAMPLES$
    describe the attempt being corrected rather than the original generation output --
    without that the rounds do not actually chain.

    Rounds stop as soon as the best score reaches SCORE_DONE_THRESHOLD, the same
    criterion that decides whether critique runs at all.

    Returns (crit_info, attempts) exactly like crit(), where crit_info is the round that
    produced the best score and attempts is every critique attempt across all rounds.
    """
    rounds = max(1, int(getattr(args, "critique_rounds", 1) or 1))
    result_path = _critique_result_path(args, main_folder_base, case_path)
    crit_out = f"{main_folder_base}/length{case_path}/target_multisource_critique_history.csv"

    # Stop after this many consecutive rounds that fail to beat the best score so far.
    # Reuses --early-stopping (default 5); --no-early-stopping disables it. With
    # --critique-rounds set high (40), this plateau check -- not the round cap -- is what
    # normally ends a case, so the budget is spent only while refinement is still paying.
    no_improve_limit = (None if getattr(args, "no_early_stopping", False)
                        else getattr(args, "early_stopping", 5))
    no_improve = 0

    all_attempts = []
    # Two different "bests", previously conflated into one variable:
    #   best_score  -- best across the generation attempt AND every critique round;
    #                  drives the stop check and which attempt is fed back as context.
    #   best_round_* -- best among the CRITIQUE rounds only; crit_info must be a critique
    #                  result, so this is what gets returned.
    # Collapsing them made round 1 unconditionally become "best" even when it scored
    # BELOW the generation attempt, so later rounds were told a worse attempt was best.
    best_info = None
    best_round_score = -1.0
    best_score = ms_score
    best_csv = None                     # None => generation output already in place
    best_ctx = {
        "iteration": "Best so far (generation)",
        "label": "best scoring attempt",
        "operation_history": str(operation_history),
        "code": ms_code, "score": ms_score,
        "nl_score": ms_nl_score, "generated_samples": ms_generated_samples,
    }
    latest_ctx = None

    for rnd in range(1, rounds + 1):
        if rnd > 1:
            if best_score >= SCORE_DONE_THRESHOLD:
                print(f"[critique] round {rnd}: best score {best_score:.4f} >= "
                      f"{SCORE_DONE_THRESHOLD} — stopping")
                break
            if no_improve_limit is not None and no_improve >= no_improve_limit:
                print(f"[critique] round {rnd}: no score improvement for "
                      f"{no_improve} rounds — stopping")
                break
            # Stage the attempt being corrected so $RES_*$ describes it, not the original.
            if result_path and best_csv and os.path.exists(best_csv):
                try:
                    shutil.copy2(best_csv, result_path)
                except Exception as exc:
                    print(f"[critique] round {rnd}: could not stage {best_csv}: {exc}")
            blocks = [best_ctx] + ([latest_ctx] if latest_ctx is not None else [])
            past_context_str = format_past_attempts(blocks)

        crit_info, attempts = crit(
            args, length, case, operation_history, past_context_str,
            judge_reason=judge_reason, budget=budget,
        )
        all_attempts.extend(attempts)

        # Archive this round's output; critique overwrites one fixed CSV every round.
        round_csv = (f"{main_folder_base}/length{case_path}"
                     f"/target_multisource_critique_round{rnd}.csv")
        if os.path.exists(crit_out):
            try:
                shutil.copy2(crit_out, round_csv)
            except Exception:
                round_csv = None
        else:
            round_csv = None

        # Persist this round immediately. The driver's _CASE_TIMEOUT KILLS the worker,
        # and the case record used to be written only after ALL rounds finished -- so a
        # timeout threw away every completed round, including ones that had already
        # produced a correct result (26 L6 cases were lost that way, 0 of them leaving a
        # JSON). Flushing per round means a kill costs at most the round in flight.
        if on_round is not None:
            try:
                on_round(attempts)
            except Exception as exc:
                print(f"[critique] round {rnd}: flush failed: {exc}")

        top = max(attempts, key=lambda a: a["score"]) if attempts else None
        round_score = top["score"] if top else 0.0
        print(f"[critique] round {rnd}/{rounds}: score={round_score:.4f} "
              f"correct={bool(crit_info[0])} (best so far {best_score:.4f})")

        if best_info is None or round_score > best_round_score:
            best_info, best_round_score = crit_info, round_score
        if round_score > best_score:
            # Only stage/report a round as overall-best when it actually beats the
            # generation attempt too.
            no_improve = 0
            best_score, best_csv = round_score, round_csv
            if top is not None:
                best_ctx = {
                    "iteration": f"Best so far (critique round {rnd})",
                    "label": "best scoring attempt",
                    "operation_history": str(operation_history),
                    "code": top.get("code", ""), "score": round_score,
                    "nl_score": top.get("nl_score", ""),
                    "generated_samples": top.get("generated_samples", ""),
                }
        else:
            no_improve += 1

        if top is not None:
            latest_ctx = {
                "iteration": f"Most recent (critique round {rnd})",
                "label": "most recent attempt",
                "operation_history": str(operation_history),
                "code": top.get("code", ""), "score": round_score,
                "nl_score": top.get("nl_score", ""),
                "generated_samples": top.get("generated_samples", ""),
            }

        # NO break on crit_info[0]. That flag is the ground-truth test verdict, and
        # stopping on it would let the answer decide when to stop searching -- an oracle
        # a real deployment does not have, which would also make the round counts (and
        # therefore the cost) unreproducible without labels. Rounds end only on
        # score-visible signals: score >= SCORE_DONE_THRESHOLD, the no-improvement
        # plateau, the round cap, or the per-case timeout.

    # Restore the best round's output so downstream validation/scoring sees it.
    if best_csv and os.path.exists(best_csv):
        try:
            shutil.copy2(best_csv, crit_out)
        except Exception:
            pass

    # Drop every per-round archive now that the best one has been restored. These exist
    # ONLY to let the best round be recovered at the end; keeping them was an unbounded
    # leak -- one CSV per round per case, ~6 rounds/case at up to 1MB each, which filled
    # a 12GB filesystem partway through a 598-case sweep and killed the driver.
    for stale in glob.glob(f"{main_folder_base}/length{case_path}"
                           f"/target_multisource_critique_round*.csv"):
        try:
            os.remove(stale)
        except OSError:
            pass

    return (best_info if best_info is not None else crit_info), all_attempts


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
        choices=["hard", "soft", "history", "mcts_style"],
        help="Type of critique to perform, the actual effect is to load prompt file from prompts/{critique_type}_critique.txt. "
             "'mcts_style': MCTS-compatible critique for apple-to-apple comparison with MCTS approach",
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
    parser.add_argument("--no-critique", dest="no_critique", action="store_true", default=False,
                        help="Skip critique step — run multi-step only")
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
        choices=list(BENCHMARK_CHOICES),
        help="Benchmark dataset: 'github', 'monteprep', or 'smart_building_v2'.",
    )
    parser.add_argument(
        "--data_split",
        type=str,
        default="test",
        choices=["test", "training"],
        help="Which CSV split to use as source examples: 'test' (default) or 'training'.",
    )
    parser.add_argument(
        "--single_step_cot",
        action="store_true",
        help="Use Single Step CoT instead of Multi Step",
    )

    parser.add_argument(
        "--rag",
        type=str,
        default="none",
        choices=["none", "upper_bound", "curated_pipeline"],
        help="RAG mode: 'none' (default), 'upper_bound' (local SQLite DB from gt_csv), "
             "or 'curated_pipeline' (the static 656-pipeline corpus mcts_search uses: "
             "prefix-match the plan so far, then re-rank by cosine similarity on an "
             "8-dim structural feature vector). For --single_step_cot there is no plan "
             "yet, so the empty prefix matches everything and the re-rank returns the "
             "--rag_topk structurally most similar cases; the operator-driven arm "
             "re-retrieves before each step as MCTS does.",
    )

    parser.add_argument(
        "--curated_pipeline_db",
        type=str,
        default="rag_pipeline/db/curated_pipeline_656.db",
        help="Path to the static curated-pipeline SQLite corpus. Used when "
             "--rag curated_pipeline.",
    )

    parser.add_argument(
        "--rag_max_tokens",
        type=int,
        default=8000,
        help="Token budget for the retrieved curated-RAG block. Some corpus rows carry "
             "very large embedded samples (one is 143k tokens), so examples are dropped "
             "from the least-similar end until the block fits rather than overflowing "
             "the prompt.",
    )

    parser.add_argument(
        "--curated_pipeline_norm_stats",
        type=str,
        default="rag_pipeline/db/curated_pipeline_features.norm_stats.json",
        help="Per-dimension mean/std the corpus feature vectors were normalized with, "
             "so a new query vector lands in the same space. Used when "
             "--rag curated_pipeline.",
    )

    parser.add_argument(
        "--gt_csv",
        type=str,
        default="ground_truth_pipelines.csv",
        help="Path to ground-truth CSV used to build the upper_bound RAG DB. "
             "Defaults to ground_truth_pipelines.csv.",
    )

    parser.add_argument(
        "--iterative",
        type=int,
        default=None,
        help="Number of full ms+critique iterations per case. Defaults to 1 unless --budget is set. "
             "In iterations >=2, past operation history, code, and score are injected into prompts.",
    )

    parser.add_argument(
        "--critique-rounds",
        dest="critique_rounds",
        type=int,
        default=1,
        help="ReAct-style refinement: run generation ONCE, then up to N critique rounds "
             "on its output. Each round is told the best-scoring attempt so far and the "
             "most recent one (code, score, output samples, score analysis), and rounds "
             "stop as soon as the score reaches the done threshold. Distinct from "
             "--iterative, which repeats generation+critique as a unit. Default 1 "
             "reproduces the single-critique behaviour exactly.",
    )

    parser.add_argument(
        "--plain",
        action="store_true",
        default=False,
        help="Disable past run context injection in iterative experiments. "
             "When enabled, each iteration runs independently without context from previous iterations.",
    )

    parser.add_argument(
        "--reward",
        type=str,
        default="score",
        choices=["score", "partial"],
        help="Reward mechanism for scoring past iterations. "
             "'score' uses full eval_score (default). "
             "'partial' counts matched columns against ground truth.",
    )

    parser.add_argument(
        "--early-stopping",
        dest="early_stopping",
        type=int,
        default=5,
        help="Stop iterating early if score has not improved for this many consecutive iterations.",
    )

    parser.add_argument(
        "--no-early-stopping",
        dest="no_early_stopping",
        action="store_true",
        default=False,
        help="Disable early stopping (score-plateau check). "
             "Useful for budget experiments where only budget and reward-True control stopping.",
    )

    parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Per-case cost budget in dollars. Stop iterating when cumulative cost exceeds this limit. "
             "When set without --iterative, runs as many iterations as the budget allows (up to a safety cap).",
    )

    parser.add_argument(
        "--rule-hints",
        dest="rule_hints",
        action="store_true",
        default=False,
        help="Inject the MCTS rule engine's top-ranked JOIN and GROUP_BY candidates "
             "into the prompts as hints (see hints/rule_hints.py). Ranked once per "
             "case at depth 0, so no extra LLM calls are made.",
    )

    parser.add_argument(
        "--rule-hints-top-k",
        dest="rule_hints_top_k",
        type=int,
        default=3,
        help="How many rule-engine candidates of each type (JOIN, GROUP_BY) to inject. "
             "Defaults to 3, matching MCTS's _RULE_INJECT_TOP_K.",
    )

    parser.add_argument(
        "--memory_granularity",
        type=str,
        default="summary",
        choices=["summary", "response", "qa"],
        help=(
            "Controls how much context from each completed operator step is carried into "
            "the next step's prompt. "
            "'summary': compact extracted result only (default). "
            "'response': full LLM response at each step including brief reasoning. "
            "'qa': full prompt + response at each step including brief reasoning."
        ),
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


_CASE_TIMEOUT = int(os.environ.get("CRITIQUE_CASE_TIMEOUT", 600))  # 10 minutes per case by default

# Score at or above which an attempt is treated as done: critique is skipped and the
# iteration loop stops. 1.0 means "only a perfect score counts as done".
#
# This was 0.9, which misfires badly under --data_split training: the benchmark ships no
# training-side target, so the training output is scored against target.csv (the GT
# pipeline's output on the TEST sources) and a CORRECT script tops out around ~0.91.
# Wrong-but-close outputs therefore land in 0.90-0.95 routinely, clear the gate, and are
# declared done without ever being critiqued. Measured on L3: 6 such misfires in the
# materialization arm vs 2 in plain -- materialization produces closer-but-still-wrong
# output, so it was penalised precisely for improving.
SCORE_DONE_THRESHOLD = 1.0


def _flush_json(case_record, json_path):
    """Atomically overwrite the per-case JSON with current case_record."""
    try:
        tmp_path = json_path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(case_record, f, indent=2, default=str)
        os.replace(tmp_path, json_path)
    except Exception as e:
        print(f"Warning: failed to flush JSON to {json_path}: {e}")


def _critique_case_worker(args, length, case, result_queue):
    """Runs one SSCoT/multistep+critique case fully in a child process."""
    try:
        # Become a process-group leader so the driver can kill this worker AND every
        # process it started. The worker is non-daemon (it must spawn the scorer, which
        # in turn spawns the FD tool), so killing it alone leaves those grandchildren
        # orphaned onto init, spinning at 100% CPU on large tables until the machine is
        # rebooted. Killing the group takes the whole tree down.
        try:
            os.setsid()
        except OSError:
            pass  # already a group leader
        case_path = f"{length}_{case}"
        main_folder_base = resolve_main_folder(getattr(args, "benchmark", "github"))
        code_path = f"{main_folder_base}/length{case_path}/python_recovered.py"

        # Resolve num_iterations: explicit flag > budget mode > default
        budget = getattr(args, "budget", None)
        _iterative_arg = getattr(args, "iterative", None)
        if _iterative_arg is not None:
            num_iterations = _iterative_arg          # explicit cap set by user
        elif budget is not None:
            num_iterations = 10_000                  # effectively unlimited; budget controls stopping
        else:
            num_iterations = 1                       # backward-compatible default

        # Resolve early stopping: check for --no-early-stopping flag
        if getattr(args, "no_early_stopping", False):
            NO_IMPROVE_LIMIT = None                 # disabled
        else:
            NO_IMPROVE_LIMIT = getattr(args, "early_stopping", 5)

        past_attempts = []
        succeeded = False
        case_record = {"case": case_path, "iterations": []}
        json_path = f"{args.json_directory}/{case_path}.json"
        best_score_so_far = -1.0
        no_improve_count = 0
        cumulative_ms_cost = 0.0   # Track cumulative MS cost across iterations
        cumulative_crit_cost = 0.0  # Track cumulative critique cost across iterations

        # Clean up artifacts from previous runs of this case to ensure clean slate
        files_to_clean = [
            f"{main_folder_base}/length{case_path}/python_recovered.py",
            f"{main_folder_base}/length{case_path}/target_multisource.csv",
            f"{main_folder_base}/length{case_path}/target_multisource_cot.csv",
            f"{main_folder_base}/length{case_path}/target_multisource_critique_history.csv",
        ]
        print(f"[CLEANUP] case={case_path} — removing stale artifacts before first iteration")
        for file_path in files_to_clean:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"[CLEANUP]   deleted: {file_path}")
                else:
                    print(f"[CLEANUP]   not found (ok): {file_path}")
            except Exception as e:
                print(f"[CLEANUP] Warning: Could not remove {file_path}: {e}")

        # Create llm_client here (subprocess cannot share the parent's client)
        _token_tracker = TokenUsageTracker()
        _case_logger = create_logger("JUDGE", args.log_directory, length, case, case)
        _llm_client = LLMClient(model=args.model, tracker=_token_tracker, logger=_case_logger, cost_budget=budget if budget is not None else 0.0)

        try:
            for iter_num in range(1, num_iterations + 1):
                past_context_str = format_past_attempts(past_attempts)

                ms_start_time = time.time()
                # Pass None to ms() so each iteration gets fresh trackers for MS step
                # (to keep per-iteration costs correct in JSON)
                # Pass budget so that LLMClient in multi_step/single_step_cot can enforce pre-call checks
                try:
                    ms_info, operation_history, ms_extras = ms(
                        args, length, case, args.log_directory, args.experiment_name, past_context_str, token_tracker=None, budget=budget
                    )
                except CostBudgetExceeded as e:
                    print(f"[iter {iter_num}] Stopping: {e}")
                    _flush_json(case_record, json_path)
                    raise
                ms_execution_time_ms = (time.time() - ms_start_time) * 1000
                result = (case_path,) + ms_info

                # Precompute CSV head for ms attempt (used in both early-success and critique paths)
                ms_csv_head = ""
                if ms_extras is not None:
                    try:
                        df_ms = ms_extras[0]
                        if df_ms is not None and len(df_ms) > 0:
                            ms_csv_head = df_ms.head(10).to_csv(index=False)
                    except Exception:
                        pass

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
                reward_mode = getattr(args, "reward", "score")

                # Always compute score upfront; used to gate critique when reward="score"
                try:
                    ms_nl_score, ms_generated_samples, ms_score, ms_score_timing = _compute_attempt_context(
                        f"{main_folder_base}/length{case_path}/target_multisource.csv",
                        f"{main_folder_base}/length{case_path}/target.csv",
                        args.target_length,
                        precomputed=ms_extras,
                        reward_mode=reward_mode,
                        length=length,
                    )
                except Exception:
                    ms_nl_score, ms_generated_samples, ms_score, ms_score_timing = "", [], 0.0, {}

                if reward_mode == "score":
                    enact_critique = ms_score < SCORE_DONE_THRESHOLD
                    print(f"[iter {iter_num}] ms_score={ms_score:.4f} — "
                          f"{'running critique' if enact_critique else f'skipping critique (score >= {SCORE_DONE_THRESHOLD})'}")
                else:
                    enact_critique = not result[1]
                    if args.judge != "gt":
                        df_generated_path = f"{main_folder_base}/length{case_path}/target_multisource.csv"
                        df_ground_truth_path = f"{main_folder_base}/length{case_path}/target.csv"
                        try:
                            df_generated = pd.read_csv(df_generated_path, low_memory=False)
                            df_ground_truth = pd.read_csv(df_ground_truth_path, low_memory=False)
                            drop_leading_index_col_if_present(df_ground_truth)
                            is_correct, judge_reason = judge(df_generated, df_ground_truth, args.judge, _llm_client, logger=_case_logger)
                            enact_critique = not is_correct
                        except CostBudgetExceeded as e:
                            print(f"[iter {iter_num}] Stopping: {e}")
                            _flush_json(case_record, json_path)
                            raise
                        except Exception as e:
                            print(f"Judge failed for {case_path}, falling back to gt: {e}")
                            enact_critique = not result[1]

                if not enact_critique:  # output judged as correct or score >= threshold
                    shutil.copy2(code_path, f"{main_folder_base}/length{case_path}/python_recovered_successful.py")
                    print("Success!")
                    succeeded = True
                    # Record MS-only iteration (no critiques ran)
                    # ms_nl_score, ms_score, etc. already computed above
                    case_record["iterations"].append({
                        "iteration": iter_num,
                        "ms": {
                            "is_correct": bool(ms_info[0]),
                            "score": ms_score,
                            "cost": ms_info[4] if len(ms_info) > 4 else 0.0,
                            "latency": ms_info[5] if len(ms_info) > 5 else 0.0,
                            "nl_score": ms_nl_score,
                            "generated_samples": ms_generated_samples,
                            "code": code,
                            "generated_csv_head": ms_csv_head,
                            "score_calculation_time_ms": ms_score_timing,
                        },
                        "critiques": [],
                        "execution_timing_ms": {
                            "multi_step": ms_execution_time_ms,
                            "critique": 0.0,
                        },
                    })
                    _flush_json(case_record, json_path)

                    # Stopping criterion 3: Score threshold reached
                    if ms_score >= SCORE_DONE_THRESHOLD:
                        print(f"[iter {iter_num}] Stopping: score {ms_score:.4f} >= {SCORE_DONE_THRESHOLD} threshold.")
                        break

                    # Stopping criterion 2: Early stopping (no improvement plateau)
                    if NO_IMPROVE_LIMIT is not None:
                        if ms_score > best_score_so_far:
                            best_score_so_far = ms_score
                            no_improve_count = 0
                        else:
                            no_improve_count += 1
                            if no_improve_count >= NO_IMPROVE_LIMIT:
                                print(f"Early stopping: score did not improve for {NO_IMPROVE_LIMIT} iterations.")
                                break
                    else:
                        # Even if early stopping is disabled, still track best score for context
                        if ms_score > best_score_so_far:
                            best_score_so_far = ms_score

                    # Stopping criterion 4: Per-case cost budget exceeded
                    # ms_info[4] NOW contains ACTUAL total cost spent (not averaged)
                    if budget is not None:
                        ms_cost_this_iteration = ms_info[4] if len(ms_info) > 4 else 0.0
                        cumulative_ms_cost += ms_cost_this_iteration
                        judge_cost = _token_tracker.cost_summary().get("total_cost", 0.0)
                        cumulative_case_cost = cumulative_ms_cost + cumulative_crit_cost + judge_cost
                        if cumulative_case_cost >= budget:
                            print(f"[iter {iter_num}] Stopping: budget ${cumulative_case_cost:.4f} >= ${budget:.4f}.")
                            break

                    # Add to past_attempts only if plain mode is disabled
                    if iter_num < num_iterations and not getattr(args, "plain", False):
                        past_attempts.append({
                            "iteration": iter_num,
                            "operation_history": str(operation_history),
                            "code": code,
                            "score": ms_score,
                            "best_attempt_type": "ms",
                            "nl_score": ms_nl_score,
                            "generated_samples": ms_generated_samples,
                        })
                    continue

                if getattr(args, 'no_critique', False):
                    break

                # For SSCoT, copy _cot.csv → target_multisource.csv so crit() can find it
                if args.single_step_cot:
                    cot_path = f"{main_folder_base}/length{case_path}/target_multisource_cot.csv"
                    ms_path  = f"{main_folder_base}/length{case_path}/target_multisource.csv"
                    try:
                        shutil.copy2(cot_path, ms_path)
                    except Exception:
                        pass

                # Build the iteration record NOW, with the generation attempt and an
                # empty critique list, and hand _run_critique_rounds a closure that
                # appends each round and flushes. If the worker is killed by
                # _CASE_TIMEOUT mid-loop, everything completed so far is already on disk.
                _crit_records = []
                _iter_rec = {
                    "iteration": iter_num,
                    "ms": {
                        "is_correct": bool(ms_info[0]),
                        "score": ms_score,
                        "cost": ms_info[4] if len(ms_info) > 4 else 0.0,
                        "latency": ms_info[5] if len(ms_info) > 5 else 0.0,
                        "nl_score": ms_nl_score,
                        "generated_samples": ms_generated_samples,
                        "code": code,
                        "generated_csv_head": ms_csv_head,
                        "score_calculation_time_ms": ms_score_timing,
                    },
                    "critiques": _crit_records,
                    "execution_timing_ms": {
                        "multi_step": ms_execution_time_ms,
                        "critique": 0.0,
                    },
                }
                case_record["iterations"].append(_iter_rec)
                _flush_json(case_record, json_path)

                def _flush_round(attempts, _rec=_crit_records, _cr=case_record, _jp=json_path):
                    _rec.extend({
                        "type": a["type"],
                        "is_correct": bool(a["is_correct"]),
                        "score": a["score"],
                        "cost": a["cost"],
                        "latency": a["latency"],
                        "nl_score": a.get("nl_score", ""),
                        "generated_samples": a.get("generated_samples", ""),
                        "code": a["code"],
                        "score_calculation_time_ms": a.get("score_calculation_time_ms", {}),
                    } for a in attempts)
                    _flush_json(_cr, _jp)

                crit_start_time = time.time()
                try:
                    crit_info, crit_attempts = _run_critique_rounds(
                        args, length, case, main_folder_base, case_path,
                        operation_history, past_context_str, judge_reason, budget,
                        ms_score=ms_score, ms_code=code, ms_nl_score=ms_nl_score,
                        ms_generated_samples=ms_generated_samples,
                        on_round=_flush_round,
                    )
                except CostBudgetExceeded as e:
                    print(f"[iter {iter_num}] Stopping: {e}")
                    _flush_json(case_record, json_path)
                    raise
                crit_execution_time_ms = (time.time() - crit_start_time) * 1000

                average_crit_path = f"{args.result_directory}/final_critique.csv"
                with open(average_crit_path, "a", newline="") as f:
                    csv.writer(f).writerow(crit_info)

                if crit_info[0]:  # critique succeeded
                    shutil.copy2(code_path, f"{main_folder_base}/length{case_path}/python_recovered_successful.py")
                    print("Success!")
                    succeeded = True

                # The record was appended before the rounds and each round flushed into
                # it as it completed; only the critique timing is still outstanding.
                _iter_rec["execution_timing_ms"]["critique"] = crit_execution_time_ms
                _flush_json(case_record, json_path)

                # Accumulate past attempt context for the next iteration (if any remain and plain mode is disabled)
                if iter_num < num_iterations and not getattr(args, "plain", False):
                    ms_attempt = {
                        "code": code,
                        "score": ms_score,
                        "type": "ms",
                        "nl_score": ms_nl_score,
                        "generated_samples": ms_generated_samples,
                    }

                    # Pick the best-scoring code across MS and all critique attempts
                    all_attempts = [ms_attempt] + crit_attempts
                    best = max(all_attempts, key=lambda a: a["score"])

                    past_attempts.append({
                        "iteration": iter_num,
                        "operation_history": str(operation_history),
                        "code": best["code"],
                        "score": best["score"],
                        "best_attempt_type": best["type"],
                        "nl_score": best.get("nl_score", ""),
                        "generated_samples": best.get("generated_samples", ""),
                    })

                iter_best_score = max([ms_score] + [a["score"] for a in crit_attempts])

                # Stopping criterion 3: Score threshold reached
                if iter_best_score >= SCORE_DONE_THRESHOLD:
                    print(f"[iter {iter_num}] Stopping: score {iter_best_score:.4f} >= {SCORE_DONE_THRESHOLD} threshold.")
                    break

                # Stopping criterion 2: Early stopping (no improvement plateau)
                if NO_IMPROVE_LIMIT is not None:
                    if iter_best_score > best_score_so_far:
                        best_score_so_far = iter_best_score
                        no_improve_count = 0
                    else:
                        no_improve_count += 1
                        if no_improve_count >= NO_IMPROVE_LIMIT:
                            print(f"Early stopping: score did not improve for {NO_IMPROVE_LIMIT} iterations.")
                            break
                else:
                    # Even if early stopping is disabled, still track best score for context
                    if iter_best_score > best_score_so_far:
                        best_score_so_far = iter_best_score

                # Stopping criterion 4: Per-case cost budget exceeded
                # ms_info[4] NOW contains ACTUAL total cost spent (not averaged)
                # crit_info[1] contains the critique cost for this iteration
                if budget is not None:
                    ms_cost_this_iteration = ms_info[4] if len(ms_info) > 4 else 0.0
                    crit_cost_this_iteration = crit_info[1] if len(crit_info) > 1 else 0.0
                    cumulative_ms_cost += ms_cost_this_iteration
                    cumulative_crit_cost += crit_cost_this_iteration
                    judge_cost = _token_tracker.cost_summary().get("total_cost", 0.0)
                    cumulative_case_cost = cumulative_ms_cost + cumulative_crit_cost + judge_cost
                    if cumulative_case_cost >= budget:
                        print(f"[iter {iter_num}] Stopping: budget ${cumulative_case_cost:.4f} >= ${budget:.4f}.")
                        break

        except CostBudgetExceeded as e:
            print(f"Cost budget exceeded: {e}")
            if not succeeded:
                print("Failed!")
            result_queue.put(("ok", None))
            return

        if not succeeded:
            print("Failed!")

        # Final JSON flush (ensures complete record is on disk)
        _flush_json(case_record, json_path)

        result_queue.put(("ok", None))
    except Exception:
        result_queue.put(("error", traceback.format_exc()))


if __name__ == "__main__":

    args = get_parser().parse_args()
    args.static_hints = not args.no_static_hints
    args.majority_voting = args.no_of_runs // 2 + 1

    # set up logging
    print(args)
    experiment_log_directory, log_directory, results_directory, jsons_directory = setup_logging(
        args, args.log_dir, args.experiment_name
    )
    args.log_directory = log_directory
    args.result_directory = results_directory
    args.json_directory = jsons_directory

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
        # NOT daemon: the worker itself starts child processes (score timeout,
        # rule-hint precompute), and daemonic processes are not allowed to have
        # children. A daemon worker made every value_based score call raise
        # AssertionError into a bare `except`, silently yielding score = 0.0.
        _proc = multiprocessing.Process(
            target=_critique_case_worker,
            args=(args, length, case, _result_queue),
            daemon=False,
        )
        _proc.start()
        _proc.join(timeout=_CASE_TIMEOUT)

        if _proc.is_alive():
            print(f"[TIMEOUT] Case {case_path} exceeded {_CASE_TIMEOUT}s — killing process")
            # Kill the worker's whole process group, not just the worker: it spawns a
            # scorer, which spawns the FD tool. Killing only the worker leaves those
            # running forever as orphans. Read the pgid BEFORE terminate(), while the
            # process still exists.
            try:
                _pgid = os.getpgid(_proc.pid)
            except OSError:
                _pgid = None

            _proc.terminate()
            _proc.join(timeout=30)
            if _proc.is_alive():
                print(f"[TIMEOUT] Case {case_path} ignored terminate() — sending SIGKILL")
                _proc.kill()
                _proc.join()

            if _pgid is not None and _pgid != os.getpgid(0):
                try:
                    os.killpg(_pgid, signal.SIGKILL)
                    print(f"[TIMEOUT] Case {case_path} — killed process group {_pgid}")
                except (OSError, ProcessLookupError):
                    pass  # group already gone
        elif not _result_queue.empty():
            _status, _payload = _result_queue.get()
            if _status == "ok":
                processed_without_exceptions += 1
            else:
                print(f"Error processing case {case_path}:\n{_payload}")
        else:
            print(f"Case {case_path} exited without result")

    print(processed_without_exceptions)
