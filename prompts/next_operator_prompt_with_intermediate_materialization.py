def get_next_operator_prompt_with_intermediate_materialization(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    fd_hints,
    hints,
    all_intermediate_results,
    combine_ask_and_configure: bool,
    no_thinking: bool,
):

    assert len(all_intermediate_results) == len(
        operation_history
    ), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"
    if fd_hints.strip() == "":
        fd_hints = ""
    else:
        fd_hints = f"\nFunctional Dependency Hints:\n{fd_hints}"

    prompt_start = f"""
    query1
You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what operation should be performed next?". The operation can be performed on both the source tables and the intermediate tables if any.
Take this decision based on "operation history", intermediate tables and source, target table schema and examples.
Allowed Operations: {allowed_operation_list}.

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
 
Some useful hints:
{hints}

Operation History: 
{operation_history}
"""
    subprompts_middle = [
        f"After the {i}st/nd/rd/th operation {op}, the intermediate table is named 'intermediate_step{i}'.\nThe intermediate table schema is as follows: \n{interm.schema} \nExamples: {interm.source_samples_string}"
        for i, (interm, op) in enumerate(
            zip(all_intermediate_results, operation_history), start=1
        )
    ]
    prompt_middle = "\n".join(subprompts_middle)

    if combine_ask_and_configure:
        prompt_last = f"""
{fd_hints}
Note: The above row examples provided are only part of the corresponding rows.

More Instructions:
- Please answer with the next OPERATION following the operation history, as well as the CONFIGURATION of the next operation. 
    - For Union, it should be a list of table names; 
    - For Join, it should be a list of tables and the columns to join on, the format is [table1.join_column_from_table1, table2.join_column_from_table2]; 
    - For Group By, it should be the table and a list of columns to group by and the aggregation function to use; 
    - For PIVOT and UNPIVOT, no configuration is needed, you can set CONFIGURATION to "NONE".  
    - If you need help from tools to determine the configuration, you can set CONFIGURATION to "NONE".
- You can propose a whole plan of operations that follow the operation history. After thinking step by step, the final answer should be wrapped in two $ signs in the last single line and strictly follow this format: Next operation after operation history is $OPERATOR$ and configuration is $CONFIGURATION$.
- If the any of the schemas in source tables are almost similar, give outer Union operation first priority.
- You should only answer from allowed operations.
- If you think no more operation is needed further, please set OPERATOR to "NO_MORE_OPERATION" and CONFIGURATION to "NONE". Note that NO_MORE_OPERATION is NOT allowed when operation history is empty.
- Try not to repeat operation and it's configuration from the operation history.
    """
    else:
        prompt_last = f"""
{fd_hints}
Note: The above row examples provided are only part of the corresponding rows.

- Please answer what operation you should perform next.
- If the any of the schemas in source tables are almost similar, give outer Union operation first priority.
- Please try to make sure, using the operator history, that ALL THE COLUMNS IN THE TARGET TABLE ARE ACCOUNTED FOR.
- You should only answer from allowed operations. 
- If you think no more operation is needed further, please return 'NO_MORE_OPERATION'. Note that NO_MORE_OPERATION is NOT allowed when operation history is empty.
- Try not to repeat operation and it's configuration from the operation history.
"""

    if no_thinking:
        prompt_last += f"- The final answer should be one word wrapped in $ quotes. i.e. $OPERATOR$. No other information should be in the answer."
    else:
        prompt_last += f"- You can propose a whole plan of operations that follow the operation history. After thinking step by step, the final answer should be wrapped in two $ signs in the last single line and strictly follow this format: Next operation after operation history is $OPERATOR$."

    return [f"{prompt_start}{prompt_middle}{prompt_last}"]
