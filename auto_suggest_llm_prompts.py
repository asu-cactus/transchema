allowed_operation_list = ['JOIN', 'UNION', 'GROUP_BY', 'AGGREGATE', 'PIVOT', 'UNPIVOT', 'NO_MORE_OPERATION']

def get_next_operator_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information) :
    prompt = '''You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what operation should be performed next?". Take this decision based on "operation history" and scource, target table schema and examples.
Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}

Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.

- Please answer what operation you should perform next based on "operation history", "source" and "target" information ("schema" as well as the "examples")  in one word.
- If you feel no more operation is needed further, please return 'NO_MORE_OPERATION'.
- You should only answer from allowed operations.
- Try not to repeat operation and it's configuration from the operation history.
- the final answer should be in $ quotes. i.e. $OPERATOR$'''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information)
    return prompt


def get_join_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information, hints) :
    prompt = '''
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what tables should be joined and at which columns?". Take this decision based on "Operation History", "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}

Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.

-You may use the hint in your decision making process.
Hint : {hints}

- Please answer which tables should be joined and at which columns that hasn't appeared yet in "operation history".
- You should only answer from available columns of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- Only return two tables that should be joined and on which columns.
- The final answer should be in format of list.
- The first element of list should be the list of two tables that should be joined.
- The next elements should be list of two columns on which the join should be perfomed.
- i.e. [ [table1, table2], [table1.join_column1,table2.join_column1], [table1.join_column2,table2.join_column2],...]
- The final answer list should be within $ quotes strictly. [i.e. $ Final Answer List $]
    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information,hints = hints)
    return prompt

def get_group_by_aggregate_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information, hints) :
    prompt = '''
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "1. Which column should be used for Group By operation? 2. Which column should be Aggregated? 3.Which Aggregation function should be used?". Take this decision based on "Operation History", "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}

Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.

-You may use the hint in your decision making process.
Hint : {hints}

- Please answer on which columns "Group By" operation should be performed, on which column aggregation should be performed and which aggregation function. 
- You should only answer from available columns of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in list where initial elements are group by columns, next element is aggregation column and next element is aggregation function. Also quote all element in $. i.e. [ $group_by_columns$, $aggregate_column$, $aggregation_function$].
- Strictly follow the answer format. All elements of list should be within $ quotes.
    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information,hints = hints)
    return prompt

def get_union_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information) :
    prompt = '''
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what tables should be Union-ed?". Take this decision based on "Operation History", "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}

Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.

- Please answer which tables should be unioned.
- Try not to repeat operation and it's configuration. i.e. Union on tables should only appear once in "Operation History".
- You should only answer from available tables of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in format of list where elements are quoted by $. I.e. [$table1$, $table2$, ...].
    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information)
    return prompt

def get_python_script(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information_with_location, target_file_location) :
    prompt = '''
    You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in 'operation_history' list . The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 

    Operation History: {operation_history}

    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Multi Source Information: {source_information_with_location}

    5. Write the result to this path {target_file_location}

    Transformation Plan:
 - Provide a detailed plan, step by step for transforming the data from the source tables to match the target table format.
 - You are strictly required to perform all the operations mentioned in the "Operations History" list. 
 - You may consider the "Source" and "Target" schema and examples to build correct pipeline.
 - You may use more operations, but the ones in "Operations History" should always be covered and in that sequence.
 - You may use string conversions or date conversions if needed.
 - Make sure that table generated through the script has the same column structure as target.

  Python Script:
 - Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths.
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 Please quote the Python script between one single "```Python" and "```".

    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information_with_location=source_information_with_location, target_file_location = target_file_location)

    return prompt

# Plan : 
# - Each step could be something similar to the following candidate steps:
#  (1) union two tables that have similar schemas and non-overlapping tuples.
#  (2) join two tables that have shared columns with overlapping values.
#  (3) aggregation
#  (4) selection or filtering
#  (5) applying a projection
#  (6) applying a transformation function.