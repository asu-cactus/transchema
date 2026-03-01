def get_cot_prompt(
    target_data_name,
    target_data_schema,
    target_samples,
    source_information,
    save_path,
    error_string,
):
    err = ""
    if len(error_string) > 0:
        err = f"Error in previous attempt : {error_string}"
    prompt = """You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table. The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 


Your Task Details:
1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: 
    {source_information}

5. Write the result to this path: {save_path}

Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.

Transformation Plan:
- Provide a detailed plan, step by step for transforming the data from the source tables to match the target table format. 
- Each step should be a concrete data manipulation, such as a query.
- Each step could be something similar to the following candidate steps:
(1) union two tables that have similar schemas and non-overlapping tuples.
(2) join two tables that have shared columns with overlapping values.
(3) aggregation
(4) selection or filtering
(5) applying a projection
(6) applying a transformation function.


Python Script:
- Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths.
- Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
Please STRICTLY quote the Python script between "```Python" and "```"
- If source tables have simialr schema and dissimilar keys, we shall use union (concat)
- If source tables have similar schema and similar keys, we shall use join (in most cases, inner join rather than outer join should be used)
- Do not add any print statements in the script.
{err}
""".format(
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information=source_information,
        save_path=save_path,
        err=err,
    )

    return [prompt]
