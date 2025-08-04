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
):
    prompt = """
    query1
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what operation should be performed next?". Take this decision based on "operation history", the schema of the source, target tables, and examples in the target table.
Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
{fd_hints}

{hints}

Note: The row examples provided are part of the corresponding rows.

- Please answer what operation you should perform next based on "operation history", "source tables" and "target tables" information ("schema" as well as the "examples")  in one word.
- If there are any source tables having similar schemas, give outer Union operation first priority.
- Please try to make sure, using the operator history, that ALL THE COLUMNS IN THE TARGET TABLE ARE ACCOUNTED FOR.
- If you feel no more operation is needed further, please return 'NO_MORE_OPERATION'.
- You should only answer from allowed operations.
- Try not to repeat operation and it's configuration from the operation history.
- the final answer should be in $ quotes. i.e. $OPERATOR$""".format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
        fd_hints=fd_hints,
        hints=hints[0],
    )
    return [prompt]
