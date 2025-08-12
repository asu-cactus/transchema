def get_join_prompt(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    hints,
    fd_hints,
):
    prompt = """
    query1
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what tables should be joined and at which columns?". Take this decision based on "Operation History", few-shot examples, "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.


1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
5. Operation History: {operation_history}

Note: The row examples provided are part of the corresponding rows.

-You may use the hint in your decision making process.
Hint : {hints}
{fd_hints}


- Please answer which tables should be joined and at which columns that hasn't appeared yet in "operation history".
- Usually tables will be joined on shared columns. In some popular cases, the shared column(s) is/are the primary key of each table to be joined. In some other popular cases, the shared column(s) is/are the primary key of one table to be joined and the foreign key of the other table to be joined.
- You should only answer from available columns of the source tables.
- Only return two tables that should be joined and on which columns.
- Choose tables that contain columns similar to columns in the target tables to be joined.
- The final answer should be in format of list.
- The first element of list should be the list of two tables that should be joined.
- The next elements should be list of two columns on which the join should be perfomed.
- i.e. [ [table1, table2], [table1.join_column1,table2.join_column1], [table1.join_column2,table2.join_column2],...]
- The final answer list should be within $ quotes strictly. [i.e. $ Final Answer List $]
    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
        hints="",
        fd_hints=fd_hints,
    )
    return [prompt]


def get_group_by_aggregate_prompt(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    hints,
    fd_hints,
):
    prompt = """
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "1. Which columns should be used for Group By operation? 2. Which columns should be Aggregated? 3.Which Aggregation functions should be used?". Take this decision based on "Operation History", few-shot-examples, "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.


1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
5. Operation History: {operation_history}

Note: The row examples provided are part of the corresponding rows.

-You may use the hint in your decision making process.
Hint : {hints}
{fd_hints}

- If a column is part of a group by operation, it will NOT be part of an aggregation operation.
- Please answer on which columns "Group By" operation should be performed, on which columns aggregation should be performed and which aggregation functions should be used. 
- Group By columns are never float types. These Group By columns correspond to columns that are UNIQUE and non-float in the target examples, which are usually at the leftmost part of the columns of target examples.
- For Aggregate, give the aggregation function and aggregation column. Aggregation columns must not be included in group by columns. If many columns in the target table have similar integer values, it probably suggests a count aggregation should be used. If a column (such as X) has float values (such as 1211.2234 or 33.17) in the given target examples, while having integer values (such as 1001 or 35) in the given source tables, it suggests that an "average" aggregation should be applied to X, no matter how X is named. Importantly, this column X MUST BE EXCLUDED from the group by columns.
- You should only answer from available columns of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in the following format. lists where first list should be group by columns, next list should cover aggregation function and on which columns aggregations should be performed.
- Example : "group_by" = [table_name.group_by_column1, table_name.group_by_column_2, ...], "aggregations" = [aggregation_function1(table_name.aggregation_column), aggregation_function2(table_name.aggregation_column), ...]
    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
        hints="",
        fd_hints=fd_hints,
    )
    return [prompt]


def get_union_prompt(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
):
    prompt = """
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what tables should be Union-ed?". Take this decision based on "Operation History",few shot examples, "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
5. Operation History: {operation_history}

Note: The row examples provided are part of the corresponding rows.

- Please answer which tables should be unioned.
- Apply UNION to tables that have exactly the same schema without renaming columns.
- Choose tables having exactly the same schema to union.
- Try not to repeat operation and it's configuration. i.e. Union on tables should only appear once in "Operation History".
- You should only answer from available tables of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in format of list where elements are quoted by $. I.e. [$table1$, $table2$, ...].
    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
    )
    return [prompt]
