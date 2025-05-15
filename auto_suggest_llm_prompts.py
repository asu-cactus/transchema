

# Plan :
# - Each step could be something similar to the following candidate steps:
#  (1) union two tables that have similar schemas and non-overlapping tuples.
#  (2) join two tables that have shared columns with overlapping values.
#  (3) aggregation
#  (4) selection or filtering
#  (5) applying a projection
#  (6) applying a transformation function.


def get_critique_prompt(
    allowed_operation_list,
    operation_history,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    target_file_location,
    error_string,
    summary,
    python_code,
    transformed_data_schema,
    transformed_samples,
):
    prompt = """
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
    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
        target_file_location=target_file_location,
        error_string=error_string,
        python_code=python_code,
        transformed_data_schema=transformed_data_schema,
        transformed_data_examples=transformed_samples,
        summary=summary,
    )

    return [prompt]


def get_critique_prompt_with_hint(
    allowed_operation_list,
    operation_history,
    target_data_schema,
    target_samples,
    file_count,
    source_information,
    target_file_location,
    error_string,
    summary,
    python_code,
    transformed_data_schema,
    transformed_samples,
):
    prompt = """
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
    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
        target_file_location=target_file_location,
        error_string=error_string,
        python_code=python_code,
        transformed_data_schema=transformed_data_schema,
        transformed_data_examples=transformed_samples,
        summary=summary,
    )

    return [prompt]
