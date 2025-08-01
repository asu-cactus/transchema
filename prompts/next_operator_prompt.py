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
    few_shot_examples=[],
):
    prompt = """
    query1
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what operation should be performed next?". Take this decision based on "operation history" and scource, target table schema and examples and few-shot examples.
Allowed Operations: {allowed_operation_list}.

{few_shot_examples}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
5. Operation History: {operation_history}
{fd_hints}

{hints}

Note: The row examples provided are part of the corresponding rows.

- The few shot examples have the examples with similar schema and how their cases were handled with some explanations. 
    Few Shot Examples include Target Schema, Target Examples, Source Schema, Source Examples, and corresponding CORRECT OPERATION HISTORY used to convert Source Tables to Target. Use them in your decision process as well. Learn from the target patterns and operation history of the few shot examples and make right decisions for given question.
- Please answer what operation you should perform next based on "operation history", "source" and "target" information ("schema" as well as the "examples")  in one word.
- You may deduce the type of columns in 'Target Table' from the 'Target Examples'. Strictly make sure that the operations in 'Operation History' lead to 'Target Table' with those same type.
- If the any of the schemas in source tables are almost similar, give outer Union operation first priority.
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
        hints="",
        few_shot_examples=few_shot_examples[0],
    )
    return [prompt]
