from hints.hints_static import get_hints_section, PYTHON_SCRIPT_HINT_IDS


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
        )
    elif not operation_history:
        return get_python_script_for_single_step_cot(
            target_data_name,
            target_data_schema,
            target_samples,
            source_information_with_location,
            csv_save_path,
            error_string,
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
):
    prompt = f"""
    You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in 'operation_history' list . The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way.

    Transformation Plan:

    Operation History: {operation_history}

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
):
    prompt = f"""You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table. The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. Before generating the code, please think step by step about the transformation plan to convert the source tables to the target table.

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
{get_hints_section(PYTHON_SCRIPT_HINT_IDS, fmt="numbered")}

Please quote the Python script between one single "```Python" and "```".
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
):
    # assert len(all_intermediate_results) + 1 == len(
    #   operation_history
    # ), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"
    past_operations = operation_history[:-1] if len(operation_history) > 1 else []
    next_operation = operation_history[-1]

    prompt_start = f"""
You are writing executable Python code at runtime. The overall goal is to convert multiple source tables to the format of the target table. Some operations have already been performed, and you need to write the code for the next operation.
The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way.
    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}
    5. Write the result to this path {csv_save_path}

Past operations: {past_operations}
Next Operation : {next_operation}

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
