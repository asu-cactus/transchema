from hints.hints_static import get_hints_section, PIPELINE_HINT_IDS, PYTHON_SCRIPT_HINT_IDS, CRITIQUE_HINT_IDS
from hints.hint import get_hints


def get_python_script(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information_with_location,
    csv_save_path,
    error_string,
    all_intermediate_results,
    static_hints=False,
    past_context="",
    hint_source="",
    source_data_name_list=None,
    source_data_schema_list=None,
    directory="",
    len_idx_target_idx="",
    raw_target_schema="",
):
    if all_intermediate_results:
        return get_python_script_with_intermediate_materialization(
            operation_history,
            target_data_name,
            target_data_schema,
            target_samples,
            source_information_with_location,
            csv_save_path,
            error_string,
            all_intermediate_results,
            past_context=past_context,
        )
    elif not operation_history:
        return get_python_script_for_single_step_cot(
            target_data_name,
            target_data_schema,
            target_samples,
            source_information_with_location,
            csv_save_path,
            error_string,
            static_hints=static_hints,
            past_context=past_context,
            hint_source=hint_source,
            file_count=file_count,
            source_data_name_list=source_data_name_list,
            source_data_schema_list=source_data_schema_list,
            directory=directory,
            len_idx_target_idx=len_idx_target_idx,
            raw_target_schema=raw_target_schema,
        )
    else:
        return get_python_script_simple(
            operation_history,
            target_data_name,
            target_data_schema,
            target_samples,
            source_information_with_location,
            csv_save_path,
            error_string,
            static_hints,
            past_context=past_context,
        )


def get_python_script_simple(
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information_with_location,
    csv_save_path,
    error_string,
    static_hints=False,
    past_context="",
):
    past_context_section = f"\nPast Attempts:\n{past_context}\n" if past_context else ""
    prompt = f"""
    You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in 'operation_history' list . The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way.

    Transformation Plan:

    Operation History: {operation_history}{past_context_section}

    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}
    5. Write the result to this path {csv_save_path}

    Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths that will be used.

    Please quote the Python script between one single "```Python" and "```".
    """
    if static_hints:
        prompt += f"""
    Hints to be considered for Python code generation:
{get_hints_section(PYTHON_SCRIPT_HINT_IDS, fmt="bullet")}
 Please quote the Python script between one single "```Python" and "```"."""
    prompt += f"""
 Errors in previous Attempts : {error_string}

    """

    return [prompt]


def get_python_script_for_single_step_cot(
    target_data_name,
    target_data_schema,
    target_samples,
    source_information_with_location,
    csv_save_path,
    error_string,
    static_hints=False,
    past_context="",
    hint_source="",
    file_count=0,
    source_data_name_list=None,
    source_data_schema_list=None,
    directory="",
    len_idx_target_idx="",
    raw_target_schema="",
):
    past_context_section = f"\nPast Attempts:\n{past_context}\n" if past_context else ""
    prompt = f"""You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table. The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. Before generating the code, please think step by step about the transformation plan to convert the source tables to the target table.
{past_context_section}
    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}
    5. Write the result to this path {csv_save_path}

    Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths that will be used.

    Please quote the Python script between one single "```Python" and "```".
    """
    if static_hints:
        prompt += f"""
Hints to be considered for Python code generation:
{get_hints_section(PIPELINE_HINT_IDS, fmt="numbered")}

Please quote the Python script between one single "```Python" and "```".
"""

    # Collect data-specific hints (join, group-by, union, table matching) from hint_source
    if hint_source and hint_source not in ("none", "v2") and source_data_name_list is not None:
        hint_parts = []
        schema_for_hints = raw_target_schema if raw_target_schema else target_data_schema
        # flag=1 required for join/group_by_aggregate to produce v1_kv/v1_text formatted hints
        hint_configs = {
            "get_next_operator": (0, []),
            "join":              (1, [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]),
            "group_by_aggregate":(1, [0.8, 0.2, 0.8, 0.2, 0.8, 0.2, 0.8, 0.2, 0.8, 0.2]),
            "union":             (0, []),
        }
        for pt, (hint_flag, hints_truncate) in hint_configs.items():
            h = get_hints(
                pt,
                hint_source,
                schema_for_hints,
                file_count,
                source_data_name_list,
                source_data_schema_list,
                directory,
                len_idx_target_idx,
                hint_flag,
                hints_truncate,
            )
            if h and h[0]:
                hint_parts.extend(h)
        dynamic_hints = "\n".join(p for p in hint_parts if p)
        if dynamic_hints:
            prompt += f"""
Data-specific hints (join conditions, group-by columns, union candidates):
{dynamic_hints}

"""

    prompt += f"""
Errors in previous Attempts : {error_string}
    """
    return [prompt]


def get_python_script_with_intermediate_materialization(
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information_with_location,
    csv_save_path,
    error_string,
    all_intermediate_results,
    static_hints=False,
    past_context="",
):
    # assert len(all_intermediate_results) + 1 == len(
    #   operation_history
    # ), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"
    past_operations = operation_history[:-1] if len(operation_history) > 1 else []
    next_operation = operation_history[-1]
    past_context_section = f"\nPast Attempts:\n{past_context}\n" if past_context else ""

    prompt_start = f"""
You are writing executable Python code at runtime. The overall goal is to convert multiple source tables to the format of the target table. Some operations have already been performed, and you need to write the code for the next operation.
The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way.
    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}
    5. Write the result to this path {csv_save_path}

Past operations: {past_operations}
Next Operation : {next_operation}{past_context_section}

The intermediate results of the past operations are as follows:

"""
    subprompts_middle = [
        f"After the {i}st/nd/rd/th operation {op}, the intermediate table 'intermediate_step{i}' is stored in {interm.file_path}.\nThe intermediate table schema is as follows: \n{interm.schema} \nExamples: {interm.source_samples_string}"
        for i, (interm, op) in enumerate(
            zip(all_intermediate_results, operation_history), start=1
        )
    ]
    prompt_middle = "\n".join(subprompts_middle)
    prompt_last = ""
    if static_hints:
        prompt_last += f"""

    Hints to be considered for Python code generation:
 - Please write python code to execute the next operation {next_operation}.
{get_hints_section(PYTHON_SCRIPT_HINT_IDS, fmt="bullet")}
"""
    prompt_last += f"""
  Errors in previous Attempts : {error_string}
    """
    return [f"{prompt_start}{prompt_middle}{prompt_last}"]
