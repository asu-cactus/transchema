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
import pandas as pd
from eval_score.score import relative_csv_score
from llm.llm_models import LLMClient, TokenUsageTracker

EPS = 1e-2  # true_combined_score must exceed 1 - EPS to be considered correct


def judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, judge_type: str, llm_client: LLMClient) -> bool:
    if judge_type == "gt":
        raise ValueError("gt judge is handled upstream via compare_lists_matching — don't call judge() for it")
    elif judge_type == "det_score":
        return score_judge(df_generated, df_ground_truth)
    elif judge_type == "llm":
        return llm_judge(df_generated, df_ground_truth, llm_client)
    elif judge_type == "llm_score":
        return llm_score_judge(df_generated, df_ground_truth, llm_client)
    elif judge_type == "llm_score_hybrid":
        return llm_nl_score_judge(df_generated, df_ground_truth, llm_client)
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


def score_judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame) -> bool:
    """
    Pure deterministic judge. Uses true_combined_score = (fd_f1 + col_ratio) / 2.
    Returns True (correct) iff score >= 1 - EPS.
    """
    _, _, _, _, true_combined_score, _ = _score_tuple(df_generated, df_ground_truth)
    print(f"DET_SCORE: true_combined_score={true_combined_score:.4f}, threshold={1.0 - EPS:.4f}, result={true_combined_score >= (1.0 - EPS)}")
    return true_combined_score >= (1.0 - EPS)


def llm_judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, llm_client: LLMClient) -> bool:
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
    Consider: schema match (column names, types), value correctness, row count, and structural integrity.

    Respond ONLY with a JSON object in this exact format (no markdown, no preamble):
    {{"correct": true, "reason": "brief explanation"}}
    or
    {{"correct": false, "reason": "brief explanation"}}"""

    response_str = llm_client.gpt(prompt)[0]
    return _parse_llm_bool_response(response_str)


def llm_score_judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, llm_client: LLMClient) -> bool:
    """
    LLM sees both tables + raw numeric score metrics.
    Returns True if LLM judges correct.
    """
    fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict = \
        _score_tuple(df_generated, df_ground_truth)

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

    Respond ONLY with a JSON object in this exact format (no markdown, no preamble):
    {{"correct": true, "reason": "brief explanation"}}
    or
    {{"correct": false, "reason": "brief explanation"}}"""

    response_str = llm_client.gpt(prompt)[0]
    return _parse_llm_bool_response(response_str)


def llm_nl_score_judge(df_generated: pd.DataFrame, df_ground_truth: pd.DataFrame, llm_client: LLMClient) -> bool:
    """
    LLM sees both tables + natural language interpretation of the score.
    Softer signal than raw numbers — tells the LLM what the score *means*.
    Returns True if LLM judges correct.
    """
    fd_ratio, col_ratio, combined_score, fd_f1, true_combined_score, debug_dict = \
        _score_tuple(df_generated, df_ground_truth)

    nl_interpretation = _build_nl_score_interpretation(
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

    Respond ONLY with a JSON object in this exact format (no markdown, no preamble):
    {{"correct": true, "reason": "brief explanation"}}
    or
    {{"correct": false, "reason": "brief explanation"}}"""

    response_str = llm_client.gpt(prompt)[0]
    return _parse_llm_bool_response(response_str)

def _build_nl_score_interpretation(
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
    lines.append(f"Combined score (fd_f1 + col_ratio) / 2 = {true_combined_score:.3f} (1.0 is perfect).")

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

    # --- Column mapping ---
    col_info = debug_dict.get("columns", {})
    if col_ratio >= 1.0 - EPS:
        lines.append("Column mapping is complete — all ground truth columns are accounted for.")
    else:
        lines.append(f"Column coverage ratio: {col_ratio:.3f} — some ground truth columns are missing or misnamed.")
        a_to_b = col_info.get("A_to_B", {})
        b_to_b = col_info.get("B_to_B", {})
        lines.append(
            f"Generated→GroundTruth column matches: {a_to_b.get('count', '?')} / {b_to_b.get('count', '?')}."
        )

    return "\n".join(lines)

def _parse_llm_bool_response(response_str: str) -> bool:
    print(f"JUDGE RAW RESPONSE: {repr(response_str)}")
    
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
        print(f"JUDGE PARSED RESULT: {result}")
        return result
    except (json.JSONDecodeError, KeyError):
        lower = response_str.lower()
        if '"correct": true' in lower or '"correct":true' in lower:
            print("JUDGE PARSED RESULT: True (fallback grep)")
            return True
        print("JUDGE PARSED RESULT: False (parse failed, conservative default)")
        return False
