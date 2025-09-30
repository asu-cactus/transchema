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

    #assert len(all_intermediate_results) == len(
     #   operation_history
    #), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"
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
4. Source Information: {source_information}
 
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
    - If there is only one source table, UNION should not be an option;
    - For Union, it should be a list of table names; 
    - For Join, it should be a list of tables and the columns to join on, the format is [table1.join_column_from_table1, table2.join_column_from_table2]; 
    - For Group By, it should be the table and a list of columns to group by and the aggregation function to use; 
    - For PIVOT and UNPIVOT, no configuration is needed, you can set CONFIGURATION to "NONE".  
    - If you need help from tools to determine the configuration, you can set CONFIGURATION to "NONE".
- You can propose a whole plan of operations that follow the operation history. After thinking step by step, the final answer should be wrapped in two $ signs in the last single line and strictly follow this format: Next operation after operation history is $OPERATOR$ and configuration is $CONFIGURATION$.
- If any two source tables have different columns, DO NOT give the UNION operation.
- If there are multiple source tables and the target table having exactly same columns, give Union operation first priority .
- If there are two source tables with different schemas that share one or a few common columns, which exist in the target data, give Join operation first priority.
- If multiple source tables share the same schema while the target table (i.e., target examples) also share the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key.
- Many data transformation pipelines contain a GROUP BY operator at the very end.
- You should only answer from allowed operations.
- If you think no more operation is needed further, please set OPERATOR to "NO_MORE_OPERATION" and CONFIGURATION to "NONE". Note that NO_MORE_OPERATION is NOT allowed when operation history is empty.
- Try not to repeat operation and it's configuration from the operation history.
    """
    else:
        prompt_last = f"""
{fd_hints}

- Please answer what operation you should perform next based on "operation history", "source tables" and "target tables" information ("schema" as well as the "examples")  in one word.
- If any two source tables have different columns, DO NOT give the UNION operation.
- If there are multiple source tables and the target table having exactly same columns, give Union operation first priority .
- If there are two source tables with different schemas that share one or a few common columns, which exist in the target data, give Join operation first priority.
- If multiple source tables share the same schema while the target table (i.e., target examples) also share the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key.
- Many data transformation pipelines contain a GROUP BY operator at the very end, particularly if the leftmost columns in the intermediate result contain a lot of duplicate values. 
- Please try to make sure, using the operator history, that ALL THE COLUMNS IN THE TARGET TABLE ARE ACCOUNTED FOR.
- You should only answer from allowed operations. 
- If you think no more operation is needed further, please return 'NO_MORE_OPERATION'. Note that NO_MORE_OPERATION is NOT allowed when operation history is empty.
- Try not to repeat operation and it's configuration from the operation history.
"""

    if no_thinking:
        prompt_last += f"- To faciliate the parsing of the operation, the final answer should be in $ quotes. i.e. $OPERATOR$, such as $JOIN$, $UNION, $GROUP_BY/AGGREGATE$ in a single line"
    else:
        prompt_last += f"- You can propose a whole plan of operations that follow the operation history. After thinking step by step. To faciliate the parsing of the operation, the final answer should be in $ quotes. i.e. $OPERATOR$, such as $JOIN$, $UNION, $GROUP_BY/AGGREGATE$ in a single line"

    return [f"{prompt_start}{prompt_middle}{prompt_last}"]
