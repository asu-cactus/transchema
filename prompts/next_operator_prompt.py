from hints.hints_static import get_hints_section, NEXT_OPERATOR_HINT_IDS


def get_next_operator_prompt(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    fd_hints,
    hints,
    all_intermediate_results: dict = {},
    static_hints=False,
    past_context="",
    intermediate_scores: dict = {},
):
    past_context_section = f"\nPast Attempts:\n{past_context}\n" if past_context else ""
    prompt_start = f"""
    query1
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what operation should be performed next?". Take this decision based on "operation history", the schema of the source, target tables, and examples in the target table.
Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}{past_context_section}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Source Information: {source_information}

"""
    if not all_intermediate_results:
        prompt_middle = ""
    else:
        subprompts_middle = []
        for i, op in enumerate(operation_history):
            step = i + 1
            if step not in all_intermediate_results:
                continue
            interm = all_intermediate_results[step]
            score_text = ""
            if step in intermediate_scores:
                score_val, nl_score = intermediate_scores[step]
                score_text = f"\nScore against ground truth: {score_val:.3f}\n{nl_score}"
            subprompts_middle.append(
                f"After the {step}st/nd/rd/th operation {op}, the intermediate table is named 'intermediate_step{step}'.\nThe intermediate table schema is as follows: \n{interm.schema} \nExamples: {interm.source_samples_string}{score_text}"
            )
        prompt_middle = "\n".join(subprompts_middle)

    prompt_last = f"""

{fd_hints}

{hints[0]}"""

    if static_hints:
        prompt_last += (
            '\n\n- Please answer what operation you should perform next based on "operation history", '
            '"source tables" and "target tables" information ("schema" as well as the "examples")  in one word.\n'
            + get_hints_section(NEXT_OPERATOR_HINT_IDS, fmt="bullet")
            + "\n"
        )
    prompt_last += """- If you feel no more operation is needed further, please return 'NO_MORE_OPERATION'.
- You should only answer from allowed operations.
- Try not to repeat operation and it's configuration from the operation history.
- the final answer should be in $ quotes. i.e. $OPERATOR$"""
    full_prompt = f"{prompt_start}{prompt_middle}{prompt_last}"
    return [full_prompt]
