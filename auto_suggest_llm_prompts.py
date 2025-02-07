allowed_operation_list = ['JOIN', 'UNION', 'GROUP_BY', 'AGGREGATE', 'PIVOT', 'UNPIVOT', 'NO_MORE_OPERATION']

def get_next_operator_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information, fd_hints) :
    prompt = '''You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what operation should be performed next?". Take this decision based on "operation history" and scource, target table schema and examples.
Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
{fd_hints}

Note: The row examples provided are part of the corresponding rows.

- Please answer what operation you should perform next based on "operation history", "source" and "target" information ("schema" as well as the "examples")  in one word.
- Please ensure to use the internet and correspond/correlate missing data into this source table, and if needed, analyze the new table (add additional info, etc).
- You may deduce the type of columns in 'Target Table' from the 'Target Examples'. Strictly make sure that the operations in 'Operation History' lead to 'Target Table' with those same type.
- If the schemas in source tables are almost similar, give Union operation first priority.
- If you feel no more operation is needed further, please return 'NO_MORE_OPERATION'.
- You should only answer from allowed operations.
- Try to use all tables.
- Try not to repeat operation and it's configuration from the operation history.
- the final answer should be in $ quotes. i.e. $OPERATOR$'''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information, fd_hints = fd_hints)
    return [prompt]


def get_join_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information, hints, fd_hints) :
    prompt = '''
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what tables should be joined and at which columns?". Take this decision based on "Operation History", "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}

Note: The row examples provided are part of the corresponding rows.

-You may use the hint in your decision making process.
Hint : {hints}
{fd_hints}

- Please answer which tables should be joined and at which columns that hasn't appeared yet in "operation history".
- You should only answer from available columns of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- Only return two tables that should be joined and on which columns.
- The final answer should be in format of list.
- The first element of list should be the list of two tables that should be joined.
- The next elements should be list of two columns on which the join should be perfomed.
- i.e. [ [table1, table2], [table1.join_column1,table2.join_column1], [table1.join_column2,table2.join_column2],...]
- The final answer list should be within $ quotes strictly. [i.e. $ Final Answer List $]
    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information,hints = hints[0], fd_hints = fd_hints)
    return [prompt]

def get_group_by_aggregate_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information, hints, fd_hints) :
    prompt = '''
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "1. Which columns should be used for Group By operation? 2. Which columns should be Aggregated? 3.Which Aggregation functions should be used?". Take this decision based on "Operation History", "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}

Note: The row examples provided are part of the corresponding rows.

-You may use the hint in your decision making process.
Hint : {hints}
{fd_hints}

- Please answer on which columns "Group By" operation should be performed, on which columns aggregation should be performed and which aggregation functions should be used. 
- You should only answer from available columns of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in the following format. lists where first list should be group by columns, next list should cover aggregation function and on which columns aggregations should be performed.
- Example : "group_by" = [group_by_column1, group_by_column_2, ...], "aggregations" = [aggregation_function1(aggregation_column), aggregation_function2(aggregation_column), ...]
    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information,hints = hints, fd_hints = fd_hints)
    return [prompt]

def get_union_prompt(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information) :
    prompt = '''
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what tables should be Union-ed?". Take this decision based on "Operation History", "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}

Note: The row examples provided are part of the corresponding rows.

- Please answer which tables should be unioned.
- Try not to repeat operation and it's configuration. i.e. Union on tables should only appear once in "Operation History".
- You should only answer from available tables of the source tables.
- Please don't write your reasoning with the answer, just the answer would suffice.
- The final answer should be in format of list where elements are quoted by $. I.e. [$table1$, $table2$, ...].
    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information)
    return [prompt]

def get_python_script(allowed_operation_list,operation_history,target_data_name,target_data_schema,target_samples,file_count, source_information_with_location, target_file_location, error_string) :
    prompt = '''
    You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in 'operation_history' list . The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 

    Operation History: {operation_history}

    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Multi Source Information: {source_information_with_location}

    5. Write the result to this path {target_file_location}

    Transformation Plan:
 - Please ensure to use the internet and correspond/correlate missing data into this source table, and if needed, analyze the new table (add additional info, etc).
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

 Errors in previous Attempts : {error_string}

    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_name=target_data_name,target_data_schema=target_data_schema,target_samples=target_samples, source_information_with_location=source_information_with_location, target_file_location = target_file_location,error_string = error_string)

    return [prompt]

# Plan : 
# - Each step could be something similar to the following candidate steps:
#  (1) union two tables that have similar schemas and non-overlapping tuples.
#  (2) join two tables that have shared columns with overlapping values.
#  (3) aggregation
#  (4) selection or filtering
#  (5) applying a projection
#  (6) applying a transformation function.

def get_critique_prompt(allowed_operation_list,operation_history,target_data_schema,target_samples,file_count, source_information, target_file_location, error_string, summary, python_code, transformed_data_schema, transformed_samples) : 
    prompt = '''
    You are generating a data-pipeline to transform multiple source tables to target table. Upto this point, an LLM agent has created a Python Code based on Source Information, Target Information and Operations History. The python script generated didn't work properly. You will be given `Operations History`, Generated Code, Transformed Data Examples (The ones that the Python script generated) , Target Data Examples and more information about these two tables, such as Functional Dependency and Keys information. Can you add more operations to the history that can rectify the code?
You can only add operation from Allowed Operations.

Allowed Operations : {allowed_operation_list}

Operations History : {operation_history}


Python Code : ```Python
{python_code}
```

Transformed DataTable Information : 
Schema : {transformed_data_schema}
Examples : {transformed_data_examples}

Target Data Information : 
Schema : {target_data_schema}
Examples : {target_samples}
Additional Information about Target Data Table : 
    {summary}
Multi Source Information :
        {source_information}

Target File Location : {target_file_location}


Note : Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.
Column names can be confusing. Try to use examples, Functional dependency and unique columns to determine next operator.

Transformation Plan : 
- You have to transform source tables mentioned in the script to the target schema.
- Strictly avoid direct assignment operations and rely solely on generalized operations like Group By, Join, Pivot, Unpivot, Union, Join etc.
- Functional dependencies are there to guide the transformation. 
- Do not raise any error if those dependencies are not followed.
- If you add aggregation, please try to find valid reason in why you chose that aggregation function and mention that reason.
- The functional dependencies mentioned are only for the first 10 columns of the Target Data. If you feel the similar pattern is being followed in remaining columns, you may use the same operation on them as well.
- Please keep the source file location same as the python script given.
- In last step please write the result to this new path {target_file_location}

Please quote the new Python script between one single "```Python" and "```". And only write the python code into these quotes. No other information should be in these quotes.

Can you add more operations to the history that can rectify those mistakes and provide a python code that can reflect that operation history?
    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information, target_file_location = target_file_location,error_string = error_string, python_code = python_code, transformed_data_schema = transformed_data_schema, transformed_data_examples = transformed_samples,summary = summary)

    return [prompt]

def get_critique_prompt_with_hint(allowed_operation_list,operation_history,target_data_schema,target_samples,file_count, source_information, target_file_location, error_string, summary, python_code, transformed_data_schema, transformed_samples) : 
    prompt = '''
   You are generating a data-pipeline to transform multiple source tables to target table. Upto this point, an LLM agent has created a Python Code based on Source Information, Target Information and Operations History. The python script generated didn't work properly. You will be given `Operations History`, Generated Code, Transformed Data Examples (The ones that the Python script generated) , Target Data Examples and more information about these two tables, such as Functional Dependency and Keys information. Can you add more operations to the history that can rectify the code?
You can only add operation "GroupBy/Aggregation" with the aggregation function "Count" from Allowed Operations.

Allowed Operations : {allowed_operation_list}

Operations History : {operation_history}


Python Code : ```Python
{python_code}
```

Transformed DataTable Information : 
Schema : {transformed_data_schema}
Examples : {transformed_data_examples}

Target Data Information : 
Schema : {target_data_schema}
Examples : {target_samples}
Additional Information about Target Data Table : 
    {summary}
Multi Source Information :
        {source_information}

Target File Location : {target_file_location}


Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.

Transformation Plan : 
- You have to transform source tables mentioned in the script to the target schema.
- Strictly do not use direct assignment and rely solely on generalized operation Group By with aggregation function "COUNT". [i.e. Don't use statement like df["column"] = CONSTANT ]
- Functional dependencies are there to guide the transformation. 
- Do not raise any error if those dependencies are not followed.
- The functional dependencies mentioned are only for the first 10 columns of the Target Data. If you feel the similar pattern is being followed in remaining columns, you may use the same operation on them as well.
- Please keep the source file location same as the python script given.
- In last step please write the result to this new path {target_file_location}

Please quote the new Python script between one single "```Python" and "```". And only write the python code into these quotes. No other information should be in these quotes.

Please add GroupBy with Count aggregation to the history that can rectify those mistakes and provide a python code that can reflect that.
    '''.format(allowed_operation_list=allowed_operation_list,operation_history=operation_history,target_data_schema=target_data_schema,target_samples=target_samples, source_information=source_information, target_file_location = target_file_location,error_string = error_string, python_code = python_code, transformed_data_schema = transformed_data_schema, transformed_data_examples = transformed_samples,summary = summary)

    return [prompt]