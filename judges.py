# judge implementations corresponding to table 9 of datamorpher paper
#
# Judges
#
# 1. ground-truth (gt)        — binary exact match, handled upstream, not here
# 2. det_score                — deterministic score threshold
# 3. llm                      — LLM looks at both tables, returns binary verdict
# 4. llm_score                — LLM gets tables + numeric score, returns binary verdict  
# 5. llm_score_hybrid         — LLM gets tables + NL interpretation of score, returns binary verdict
#
# Input:  df_generated (DataFrame), df_ground_truth (DataFrame), llm_client (LLMClient)
# Output: bool — True = correct (do NOT enact critique), False = wrong (enact critique)

import json
import logging
import pandas as pd
from eval_score.score import relative_csv_score
from llm.llm_models import LLMClient, TokenUsageTracker

EPS = 1e-2  # true_combined_score must exceed 1 - EPS to be considered correct


def judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, judge_type: str, llm_client: LLMClient, logger: logging.Logger = None) -> tuple:
    """Returns (is_correct: bool, reason: str). reason is empty for non-LLM judges."""
    if judge_type == "gt":
        raise ValueError("gt judge is handled upstream via compare_lists_matching — don't call judge() for it")
    elif judge_type == "det_score":
        return score_judge(df_generated, df_ground_truth, logger=logger), ""
    elif judge_type == "llm":
        return llm_judge(df_generated, df_ground_truth, llm_client, logger=logger)
    elif judge_type == "llm_score":
        return llm_score_judge(df_generated, df_ground_truth, llm_client, logger=logger)
    elif judge_type == "llm_score_hybrid":
        return llm_nl_score_judge(df_generated, df_ground_truth, llm_client, logger=logger)
    else:
        raise ValueError(f"Unknown judge type: {judge_type}")


def _score_tuple(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame):
    """Run relative_csv_score, return the full 6-tuple. Callers pick what they need."""
    fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict = \
        relative_csv_score(df_generated, df_ground_truth)
    return fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict


def _df_to_prompt_str(df: pd.DataFrame, max_rows: int = 10) -> str:
    """Serialize a DataFrame to a compact string for prompt injection."""
    return df.head(max_rows).to_string(index=False)


def score_judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, logger: logging.Logger = None) -> bool:
    """
    Pure deterministic judge. Uses true_combined_score = (fd_f1 + col_ratio) / 2.
    Returns True (correct) iff score >= 1 - EPS.
    """
    _, _, _, _, true_combined_score, _ = _score_tuple(df_generated, df_ground_truth)
    msg = f"DET_SCORE: true_combined_score={true_combined_score:.4f}, threshold={1.0 - EPS:.4f}, result={true_combined_score >= (1.0 - EPS)}"
    if logger:
        logger.info(msg)
    else:
        print(msg)
    return true_combined_score >= (1.0 - EPS)


def llm_judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, llm_client: LLMClient, logger: logging.Logger = None) -> bool:
    """
    LLM sees both tables, no score information. Returns True if LLM judges correct.
    Expects JSON response: {"correct": true/false, "reason": "..."}
    """
    prompt = f"""You are evaluating whether a generated data table matches a ground truth table for a schema transformation task.

    Ground Truth Table (first 10 rows):
    {_df_to_prompt_str(df_ground_truth)}

    Generated Table (first 10 rows):
    {_df_to_prompt_str(df_generated)}

    Assess whether the generated table is a correct transformation of the ground truth.
    Consider: schema match (column names, types), value correctness, and structural integrity.

    Respond ONLY with a JSON object in this exact format (no markdown, no preamble):
    {{"correct": true, "reason": "brief explanation"}}
    or
    {{"correct": false, "reason": "brief explanation"}}"""

    if logger:
        logger.info(f"JUDGE_PROMPT (llm):\n{prompt}")
    response_str = llm_client.gpt(prompt)[0]
    return _parse_llm_bool_response(response_str, logger=logger)


def llm_score_judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, llm_client: LLMClient, logger: logging.Logger = None, precomputed_score: float = None) -> bool:
    """
    LLM sees both tables + raw numeric score metrics.
    Returns True if LLM judges correct.
    If precomputed_score is provided, skip re-running relative_csv_score.
    """
    if precomputed_score is not None:
        true_combined_score = precomputed_score
    else:
        _, _, _, _, true_combined_score, _ = _score_tuple(df_generated, df_ground_truth)

    score_summary = {
            "Match score based on functional dependencies and column mapping:": round(true_combined_score, 4),
    }

    prompt = f"""You are evaluating whether a generated data table matches a ground truth table for a schema transformation task.

    Ground Truth Table (first 10 rows):
    {_df_to_prompt_str(df_ground_truth)}

    Generated Table (first 10 rows):
    {_df_to_prompt_str(df_generated)}

    Similarity Metrics:
    {json.dumps(score_summary, indent=2)}

    Use the tables AND the score together to assess correctness.
    Use the provided score as the primary basis for the final decision, with a weight of 80%, and use your own internal judgment or background knowledge only as a secondary factor, with a weight of 20%.

    Respond ONLY with a JSON object in this exact format (no markdown, no preamble):
    {{"correct": true, "reason": "brief explanation"}}
    or
    {{"correct": false, "reason": "brief explanation"}}"""

    if logger:
        logger.info(f"JUDGE_PROMPT (llm_score):\n{prompt}")
    response_str = llm_client.gpt(prompt)[0]
    return _parse_llm_bool_response(response_str, logger=logger)


def llm_nl_score_judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, llm_client: LLMClient, logger: logging.Logger = None, precomputed_nl_score: str = None) -> bool:
    """
    LLM sees both tables + natural language interpretation of the score.
    Softer signal than raw numbers — tells the LLM what the score *means*.
    Returns True if LLM judges correct.
    If precomputed_nl_score is provided, skip re-running relative_csv_score.
    """
    if precomputed_nl_score is not None:
        nl_interpretation = precomputed_nl_score
    else:
        fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict = \
            _score_tuple(df_generated, df_ground_truth)
        nl_interpretation = build_nl_score_interpretation(
            fd_f1, col_ratio, true_combined_score, debug_dict
        )

    prompt = f"""You are evaluating whether a generated data table matches a ground truth table for a schema transformation task.

    Ground Truth Table (first 10 rows):
    {_df_to_prompt_str(df_ground_truth)}

    Generated Table (first 10 rows):
    {_df_to_prompt_str(df_generated)}

    Automated Scoring Analysis:
    {nl_interpretation}

    Use the tables AND the scoring analysis together to make a final correctness judgement.
    Use the provided score as the primary basis for the final decision, with a weight of 80%, and use your own internal judgment or background knowledge only as a secondary factor, with a weight of 20%.

    Respond ONLY with a JSON object in this exact format (no markdown, no preamble):
    {{"correct": true, "reason": "brief explanation"}}
    or
    {{"correct": false, "reason": "brief explanation"}}"""

    if logger:
        logger.info(f"JUDGE_PROMPT (llm_score_hybrid):\n{prompt}")
    response_str = llm_client.gpt(prompt)[0]
    return _parse_llm_bool_response(response_str, logger=logger)

def build_nl_score_interpretation(
    fd_f1: float,
    col_ratio: float,
    true_combined_score: float,
    debug_dict: dict,
) -> str:
    """
    Convert raw score metrics into a natural language paragraph the LLM can reason over.
    Emphasises key structure, equivalence classes, and FD false positives/negatives.
    """
    lines = []

    # --- Overall verdict ---

    if true_combined_score >= 1.0 - EPS:
        lines.append("Overall: the generated table appears to be a near-perfect match.")
    elif true_combined_score >= 0.75:
        lines.append("Overall: the generated table is a partial match with notable discrepancies.")
    else:
        lines.append("Overall: the generated table has significant structural differences from ground truth.")

    dist_info = debug_dict.get("distribution", {})
    js_sim_val    = dist_info.get("avg_js_similarity")
    range_ovlp    = dist_info.get("avg_range_overlap")
    if js_sim_val is not None and range_ovlp is not None:
        formula = (
            f"(fd_f1 + range_overlap + js_similarity) / 3 = "
            f"({fd_f1:.3f} + {range_ovlp:.3f} + {js_sim_val:.3f}) / 3"
        )
    elif range_ovlp is not None:
        formula = f"(fd_f1 + range_overlap) / 2 = ({fd_f1:.3f} + {range_ovlp:.3f}) / 2"
    elif js_sim_val is not None:
        formula = f"(fd_f1 + js_similarity) / 2 = ({fd_f1:.3f} + {js_sim_val:.3f}) / 2"
    else:
        formula = f"fd_f1 = {fd_f1:.3f}"
    lines.append(f"Combined score = {formula} = {true_combined_score:.3f} (1.0 is perfect).")

    # --- Key structure comparison ---
    fd_info = debug_dict.get("fd", {})
    a_info = fd_info.get("A", {})
    b_info = fd_info.get("B", {})

    keys_gen = a_info.get("keys", [])
    keys_gt  = b_info.get("keys", [])

    def fmt_keys(keys):
        if not keys:
            return "none detected"
        return "; ".join("{" + ", ".join(str(c) for c in k) + "}" for k in keys)

    lines.append(f"Ground truth candidate keys: {fmt_keys(keys_gt)}.")
    lines.append(f"Generated table candidate keys: {fmt_keys(keys_gen)}.")

    if keys_gt and keys_gen:
        # Normalise to frozensets for comparison — order-insensitive
        gt_key_set  = {frozenset(k) for k in keys_gt}
        gen_key_set = {frozenset(k) for k in keys_gen}
        missing_keys = gt_key_set - gen_key_set
        extra_keys   = gen_key_set - gt_key_set
        if not missing_keys and not extra_keys:
            lines.append("Key structure matches ground truth exactly.")
        else:
            if missing_keys:
                lines.append(
                    "Keys present in ground truth but absent in generated: "
                    + "; ".join("{" + ", ".join(str(c) for c in k) + "}" for k in missing_keys) + "."
                )
            if extra_keys:
                lines.append(
                    "Spurious keys in generated not present in ground truth: "
                    + "; ".join("{" + ", ".join(str(c) for c in k) + "}" for k in extra_keys) + "."
                )
    elif keys_gt and not keys_gen:
        lines.append("Generated table has no detectable candidate keys — ground truth has keys defined above.")
    elif keys_gen and not keys_gt:
        lines.append("Generated table introduces candidate keys not present in ground truth.")

    # --- Equivalence class comparison ---
    equiv_gen = a_info.get("equivalences", [])
    equiv_gt  = b_info.get("equivalences", [])

    def fmt_equivs(equivs):
        if not equivs:
            return "none"
        return "; ".join("{" + ", ".join(str(c) for c in eq) + "}" for eq in equivs)

    if equiv_gt or equiv_gen:
        lines.append(f"Ground truth column equivalence classes: {fmt_equivs(equiv_gt)}.")
        lines.append(f"Generated table equivalence classes: {fmt_equivs(equiv_gen)}.")

        gt_equiv_set  = {frozenset(eq) for eq in equiv_gt}
        gen_equiv_set = {frozenset(eq) for eq in equiv_gen}
        missing_equivs = gt_equiv_set - gen_equiv_set
        extra_equivs   = gen_equiv_set - gt_equiv_set

        if not missing_equivs and not extra_equivs:
            lines.append("Equivalence class structure matches ground truth exactly.")
        else:
            if missing_equivs:
                lines.append(
                    "Equivalence classes from ground truth missing in generated: "
                    + "; ".join("{" + ", ".join(str(c) for c in eq) + "}" for eq in missing_equivs) + "."
                )
            if extra_equivs:
                lines.append(
                    "Spurious equivalence classes in generated: "
                    + "; ".join("{" + ", ".join(str(c) for c in eq) + "}" for eq in extra_equivs) + "."
                )

    # --- FD-level analysis (false positives / negatives) ---
    fd_fp = fd_info.get("false_positives", [])
    fd_fn = fd_info.get("false_negatives", [])

    if fd_f1 >= 1.0 - EPS:
        lines.append("Functional dependency structure matches ground truth exactly.")
    else:
        lines.append(
            f"Functional dependency F1: {fd_f1:.3f} "
            f"(precision={fd_info.get('precision', float('nan')):.3f}, "
            f"recall={fd_info.get('recall', float('nan')):.3f})."
        )
        if fd_fp:
            fp_strs = [f"{fd['lhs']} → {fd['rhs']}" for fd in fd_fp[:5]]
            overflow = f" (and {len(fd_fp) - 5} more)" if len(fd_fp) > 5 else ""
            lines.append(f"Spurious FDs in generated (not in ground truth): {'; '.join(fp_strs)}{overflow}.")
        if fd_fn:
            fn_strs = [f"{fd['lhs']} → {fd['rhs']}" for fd in fd_fn[:5]]
            overflow = f" (and {len(fd_fn) - 5} more)" if len(fd_fn) > 5 else ""
            lines.append(f"Missing FDs from ground truth: {'; '.join(fn_strs)}{overflow}.")

    # --- Distribution analysis ---
    _DIST_THRESHOLD = 0.95
    per_col = debug_dict.get("distribution", {}).get("per_column", {})
    if not per_col:
        lines.append("No numerical columns found — distribution comparison not applicable.")
    else:
        problem_cols = {
            gt_col: info for gt_col, info in per_col.items()
            if info.get("range_overlap", 1.0) < _DIST_THRESHOLD
            or info.get("js_similarity", 1.0) < _DIST_THRESHOLD
        }
        if not problem_cols:
            lines.append("All numerical columns show complete value range overlap and matching distributions.")
        else:
            lines.append("Distribution Analysis (numerical columns with issues):")
            for gt_col, info in problem_cols.items():
                gen_col       = info["gen_col"]
                range_overlap = info.get("range_overlap", float("nan"))
                js_sim_val    = info.get("js_similarity", float("nan"))
                gs            = info["gen_stats"]
                ts            = info["gt_stats"]
                col_label = gt_col if gen_col == gt_col else f"{gen_col} (mapped to {gt_col})"
                lines.append(
                    f"  Column '{col_label}': range overlap={range_overlap:.3f}, JS similarity={js_sim_val:.3f}"
                )
                lines.append(
                    f"    Generated    — min: {gs['min']}, max: {gs['max']}, mean: {gs['mean']}"
                )
                lines.append(
                    f"    Ground Truth — min: {ts['min']}, max: {ts['max']}, mean: {ts['mean']}"
                )

    return "\n".join(lines)

def _parse_llm_bool_response(response_str: str, logger: logging.Logger = None) -> tuple:
    """Returns (is_correct: bool, reason: str)."""
    def _log(msg):
        if logger:
            logger.info(msg)
        else:
            print(msg)

    _log(f"JUDGE RAW RESPONSE: {repr(response_str)}")

    cleaned = response_str.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()

    try:
        parsed = json.loads(cleaned)
        result = bool(parsed["correct"])
        reason = parsed.get("reason", "")
        _log(f"JUDGE PARSED RESULT: {result} | REASON: {reason}")
        return result, reason
    except (json.JSONDecodeError, KeyError):
        lower = response_str.lower()
        if '"correct": true' in lower or '"correct":true' in lower:
            _log("JUDGE PARSED RESULT: True (fallback grep)")
            return True, ""
        _log("JUDGE PARSED RESULT: False (parse failed, conservative default)")
        return False, ""
