def get_python_script(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information_with_location,
    save_path,
    error_string,
):
    prompt = """
    You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in 'operation_history' list . The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 

    Operation History: {operation_history}

    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Multi Source Information: {source_information_with_location}

    5. Write the result to this path {save_path}

    Transformation Plan:
 - Please ensure to use the internet and correspond/correlate missing data into this source table, and if needed, analyze the new table (add additional info, etc).
 - Provide a detailed plan, step by step for transforming the data from the source tables so that the Transformed table is closer to the target table.
 - You are strictly required to perform all the operations mentioned in the "Operations History" list. 
 - You may consider the "Source" and "Target" schema and examples to build correct pipeline.
 - You may use more operations, but the ones in "Operations History" should always be covered and in that sequence.
 - You may use string conversions or date conversions if needed.
 - Make sure that table generated through the script has the same column structure as target.

  Python Script:
 - Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths.
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 Please quote the Python script between one single "```Python" and "```".

 Errors in previous Attempts : {error_string}

    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information_with_location=source_information_with_location,
        save_path=save_path,
        error_string=error_string,
    )

    return [prompt]


def get_python_script_with_intermediate_materialization(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information_with_location,
    save_path,
    error_string,
    all_intermediate_results,
):
    assert len(all_intermediate_results) + 1 == len(
        operation_history
    ), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"
    past_operations = operation_history[:-1] if len(operation_history) > 1 else []
    next_operation = operation_history[-1]

    prompt_start = f"""
You are writing executable Python code at runtime. The overall goal is to convert multiple source tables to the format of the target table. Some operations have already been performed, and you need to write the code for the next operation.
The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 
    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Multi Source Information: {source_information_with_location}
    5. Write the result to this path {save_path}

Past operations: {past_operations}
Next Operation : {next_operation}

The intermediate results of the past operations are saved in the following locations:
"""

    subprompts_middle = [
        f"{op}. File location: {res.file_path}"
        for op, res in zip(past_operations, all_intermediate_results)
    ]
    prompt_middle = "\n".join(subprompts_middle)

    prompt_last = f"""

    Transformation Plan:
 - Please write python code to execute the next operation {next_operation}. 
 - You should use the intermediate results of the past operations as the source tables whenever it is possible.
 - You may use string conversions or date conversions if needed.

  Python Script:
 - Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths.
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 Please quote the Python script between one single "```Python" and "```".

  Errors in previous Attempts : {error_string}
    """
    return [f"{prompt_start}{prompt_middle}{prompt_last}"]
