def get_next_operator_prompt_with_intermediate_materialization(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information,
    fd_hints,
    hints,
    all_intermediate_results,
    combine_ask_and_configure: bool,
):

    assert len(all_intermediate_results) == len(
        operation_history
    ), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"

    fd_hints = f"\nFunctional Dependency Hints:\n{fd_hints}" if fd_hints.strip() else ""

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
        f"After the {i}st/nd/rd/th operation {op}, the intermediate table schema is as follows: \n{interm.schema} \nExamples: {interm.source_samples_string}"
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
    - For Union, CONFIGURATION should be a python list of table names; 
    - For Join, CONFIGURATION should be a python list of tables and the columns to join on, the format is [table1.join_column_from_table1, table2.join_column_from_table2]; 
    - For GroupBy/Aggregation, CONFIGURATION should be the table, the column(s) to group by, the column to aggregate, and the aggregation function to use; 
    - For Pivot, CONFIGURATION should be the table and a python list of columns to pivot on;
- In your thinking process, you can propose a whole plan of operations that follow the operation history. 
- The final answer of OPERATION and CONFIGURATION should be wrapped in two $ signs in the last single line and strictly follow this format: Next operation after operation history is $OPERATOR$ and configuration is $CONFIGURATION$.
- An example output is: Next operation after operation history is $JOIN$ and configuration is $['table1.join_column_from_table1', 'table2.join_column_from_table2']$.
- If the any of the schemas in source tables are almost similar, give outer Union operation first priority.
- You should only answer from allowed operations.
- If you think no more operation is needed further, please answer with the following: Next operation after operation history is NO_MORE_OPERATION and configuration is None
    """
    else:
        prompt_last = f"""
{fd_hints}
Note: The above row examples provided are only part of the corresponding rows.

- Please answer what operation you should perform next.
- If the any of the schemas in source tables are almost similar, give outer Union operation first priority.
- Please try to make sure, using the operator history, that ALL THE COLUMNS IN THE TARGET TABLE ARE ACCOUNTED FOR.
- You should only answer from allowed operations. 
- If you think no more operation is needed further, please answer with the following: Next operation after operation history is NO_MORE_OPERATION and configuration is None
"""
    return [f"{prompt_start}{prompt_middle}{prompt_last}"]


def get_next_operator_prompt_for_ToT(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information,
    fd_hints,
    hints,
    all_intermediate_results,
    branch_factor,
):
    assert len(all_intermediate_results) == len(
        operation_history
    ), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"

    fd_hints = f"\nFunctional Dependency Hints:\n{fd_hints}" if fd_hints.strip() else ""

    output_format_str = "\n".join(
        [
            f"Operator{i}: Configuration_for_operator{i}"
            for i in range(1, branch_factor + 1)
        ]
    )

    example_output_str = """
NO_MORE_OPERATION: NONE
UNION: ['Source1', 'Source2']
JOIN: ['Source1.join_column_from_Source1', 'Source2.join_column_from_Source2']
"""
    prompt_start = f"""
    query1
Your final goal is to generate a data-pipeline to transform multiple source tables to target table and you need to answer "what operator should be performed next?". This operator can be performed on both the source tables and the intermediate tables.
You are given an operation history and going to use the tree of thoughts approach (breadth first search) to propose no more than {branch_factor} distinct operators at once, where each operator is a candidate next step right after the operation history so far.
Take this decision based on "operation history", intermediate tables and source, target table schema and examples.
Allowed Operators: 
{allowed_operation_list}

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
        f"After the {i}st/nd/rd/th operator {op}, the intermediate table schema is as follows: \n{interm.schema} \nExamples: {interm.source_samples_string}"
        for i, (interm, op) in enumerate(
            zip(all_intermediate_results, operation_history), start=1
        )
    ]
    prompt_middle = "\n".join(subprompts_middle)

    prompt_last = f"""
{fd_hints}
Note: The above row examples provided are only part of the corresponding rows.

More Instructions:
1. Before answering, think step by step about the next operators you can propose.
2. Please answer with the next OPERATOR following the operation history, as well as the CONFIGURATION of the next operator. 
    1.1 For Union, CONFIGURATION should be a list of table names; 
    1.2 For Join, CONFIGURATION should be a list of tables and the columns to join on, the format is [table1.join_column_from_table1, table2.join_column_from_table2]; 
    1.3 For GroupBy/Aggregation, CONFIGURATION should be the table, the column(s) to group by, the column to aggregate, and the aggregation function to use; 
    1.4 For Pivot, CONFIGURATION should be the table and a list of columns to pivot on; 
3. If the any of the schemas in source tables are almost similar, give outer Union operator first priority.
4. The operator should be one of the operators in the allowed operators list.
5. You can set one of the next operator to 'NO_MORE_OPERATION' (and its configuration to 'NONE') if you think it is possible that the task is done.
6. After thinking step by step, the final answer should be strictly follow this format (DO NOT add any other text such as comments):
```
Proposed next operators:
{output_format_str}
```

An example output is the following:
```
Proposed next operators:
{example_output_str}
```
    """
    prompt = f"{prompt_start}{prompt_middle}{prompt_last}"
    return [prompt]
