def get_python_script_deprecated(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information_with_location,
    save_path,
    error_string,
):
    prompt = """
    You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in 'operation_history' list . The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 

    Operation History: {operation_history}

    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Multi Source Information: {source_information_with_location}
    5. Write the result to this path {save_path}

    Transformation Plan:
 - Please ensure to use the internet and correspond/correlate missing data into this source table, and if needed, analyze the new table (add additional info, etc).
 - Provide a detailed plan, step by step for transforming the data from the source tables so that the Transformed table is closer to the target table.
 - You are strictly required to perform all the operations mentioned in the "Operations History" list. 
 - You may consider the "Source" and "Target" schema and examples to build correct pipeline.
 - You may use more operations, but the ones in "Operations History" should always be covered and in that sequence.
 - You may use string conversions or date conversions if needed.
 - Make sure that table generated through the script has the same column structure as target.
 - Please add less comments to save tokens.
 - All source tables have to be used in all cases. For example, given target examples with schema <XXXX_NUM>, and source tables with schemas A<ROW_WID,KEYWORDS_NUM>, B<ROW_WID,XXXX_NUM>, C<ROW_WID,TECHSUPPORT_NUM>, D<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, E<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, F<ROW_WID,INTERACTIONS_NUM>, G<ROW_WID,COLLECTION_EVENTS_NUM>, H<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, I<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, and J<ROW_WID,VISITS_NUM>, all source tables that have the same schema, such as D, E, H, and I must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, F, G, J, K on the shared attribute ROW_WID. Finally, it retrieves the attribute XXXX_NUM (this projection must be applied at the last step, otherwise the join column ROW_ID would be removed before applying the join)
 - Similarly, if given target examples with schema that has all attributes <Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM>, and source tables with schemas A<ROW_WID,XXXX_NUM>, B<ROW_WID,YYYY_NUM>, C<ROW_WID,ZZZZ_NUM>, D<Attr-1, ..., Attr-K>, E<Attr-1, ..., Attr-K>, F<Attr-1, ..., Attr-K>, all source tables that have the same schema, such as C, and E must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, on the shared attribute ROW_WID. Finally, it selects all attributes Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM.
  Python Script:
 - USE LESS COMMENTS IN THE SCRIPT TO SAVE TOKENS.
 - Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths.
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 Please quote the Python script between one single "```Python" and "```".

 Errors in previous Attempts : {error_string}

    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information_with_location=source_information_with_location,
        save_path=save_path,
        error_string=error_string,
    )

    return [prompt]



def get_python_script(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information_with_location,
    save_path,
    error_string,
):
    prompt = """
    You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in 'operation_history' list . The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way.

    Operation History: {operation_history}

    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}

    5. Write the result to this path {save_path}

    Transformation Plan:
 - Your code should only take the CSV file paths given in the Source Data Information as inputs.
 - You may use string conversions or date conversions if needed.
 - Note that some column names, e.g., purpose, funded_year, may not match the values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case consider the column to be aggregation, e.g., count per purpose, and sum for funded_year. They should not be used in Group By columns.
 - Make sure that table generated through the script has the same column structure as target.
 - Please answer what operation you should perform next based on "operation history", "source tables" and "target tables" information ("schema" as well as the "examples")  in one word.
 - If two source tables have different columns, DO NOT give the UNION operation.
 - If there are multiple source tables and the target table having exactly same columns, give Union operation first priority .
 - If there are two source tables with different schemas that share one or a few common columns, which exist in the target data, give Join operation first priority.
 - If multiple source tables share the same schema while the target table (i.e., target examples) also share the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key.
 - GROUP BY attribute(s) is(are) never of float types and it(they) often correspond(s) to the column(s) that has (have) all distinct/unique values in the target examples. These columns are usually at the leftmost part of the target schema. If you found a column in the target examples contain float values, do not include the column as GROUP BY attribute.
 - All source tables have to be used in all cases. For example, given target examples with schema <XXXX_NUM>, and source tables with schemas A<ROW_WID,KEYWORDS_NUM>, B<ROW_WID,XXXX_NUM>, C<ROW_WID,TECHSUPPORT_NUM>, D<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, E<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, F<ROW_WID,INTERACTIONS_NUM>, G<ROW_WID,COLLECTION_EVENTS_NUM>, H<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, I<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, and J<ROW_WID,VISITS_NUM>, all source tables that have the same schema, such as D, E, H, and I must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, F, G, J, K on the shared attribute ROW_WID. Finally, it retrieves the attribute XXXX_NUM (this projection must be applied at the last step, otherwise the join column ROW_ID would be removed before applying the join)
 - Similarly, if given target examples with schema that has all attributes <Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM>, and source tables with schemas A<ROW_WID,XXXX_NUM>, B<ROW_WID,YYYY_NUM>, C<ROW_WID,ZZZZ_NUM>, D<Attr-1, ..., Attr-K>, E<Attr-1, ..., Attr-K>, F<Attr-1, ..., Attr-K>, all source tables that have the same schema, such as C, and E must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, on the shared attribute ROW_WID. Finally, it selects all attributes Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM.
 - If duplicate tuples or duplicate keys exist in the target examples, no GROUP BY should be used.
 - If a column has integer values in one of the source tables, but the same column has float values in the target tables, an average aggregation should be applied to the column and the column should NOT be considered as GROUP BY attribute. 
 - Most source files have a numerical index column, which is always the first column, and it should be ignored in the transformation. Therefore, when reading a CSV file, please add index_col=0, e.g., sourceX = pd.read_csv('autopipeline-benchmarks/github-pipelines/lengthY_Z/test_X.csv', index_col=0)
 - Please look at the target examples, and ensure the generated data has the same type and name for each column in the target examples.

  Python Script:
 - Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths that will be used.
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 - Please do not use source files that are not mentioned in this prompt.
 Please quote the Python script between one single "```Python" and "```".

 Errors in previous Attempts : {error_string}

    """.format(
        allowed_operation_list=allowed_operation_list,
        operation_history=operation_history,
        target_data_name=target_data_name,
        target_data_schema=target_data_schema,
        target_samples=target_samples,
        source_information_with_location=source_information_with_location,
        save_path=save_path,
        error_string=error_string,
    )

    return [prompt]




def get_python_script_with_intermediate_materialization(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information_with_location,
    save_path,
    error_string,
    all_intermediate_results,
):
    #assert len(all_intermediate_results) + 1 == len(
     #   operation_history
    #), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"
    past_operations = operation_history[:-1] if len(operation_history) > 1 else []
    next_operation = operation_history[-1]

    prompt_start = f"""
You are writing executable Python code at runtime. The overall goal is to convert multiple source tables to the format of the target table. Some operations have already been performed, and you need to write the code for the next operation.
The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 
    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}
    5. Write the result to this path {save_path}

Past operations: {past_operations}
Next Operation : {next_operation}

The intermediate results of the past operations are as follows:

"""
    subprompts_middle = [
        f"After the {i}st/nd/rd/th operation {op}, the intermediate table 'intermediate_step{i}' is stored in {interm.file_path}.\nThe intermediate table schema is as follows: \n{interm.schema} \nExamples: {interm.source_samples_string}"
        for i, (interm, op) in enumerate(
            zip(all_intermediate_results, operation_history), start=1
        )
    ]
    prompt_middle = "\n".join(subprompts_middle)

    prompt_last = f"""

    Transformation Plan:
 - Please write python code to execute the next operation {next_operation}. 
 - You should use the intermediate results of the past operations as the source tables whenever it is possible.
 - You may use string conversions or date conversions if needed.
 - Make sure that table generated through the script has the same column structure as target.
 - If two source tables have different columns, DO NOT give the UNION operation.
 - If there are multiple source tables and the target table having exactly same columns, give Union operation first priority .
 - If there are two source tables with different schemas that share one or a few common columns, which exist in the target data, give Join operation first priority.
 - If multiple source tables share the same schema while the target table (i.e., target examples) also share the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key.
 - Many data transformation pipelines contain a GROUP BY operator at the very end. GROUP BY attribute(s) is(are) never of float types and it(they) often correspond(s) to the column(s) that has (have) all distinct/unique values in the target examples. These columns are usually at the leftmost part of the target schema. If you found a column in the target examples contain float values, do not include the column as GROUP BY attribute.
 - If a column is of the integer type in one of the source tables, but the same column has float values in the target tables, an average aggregation should be applied to the column and the column should NOT be considered as GROUP BY attribute.
 - If duplicata tuples exist in the given target examples, we shall not use GroupBy operators. UNION is probably used in this case.
 - All source files (excluding intermediate files) have an index column of the integer type, which is always the first column and it should be ignored in the transformation.
 - Please look at the target examples, and ensure the generated data has the same type and name for each column in the target examples. 

  Python Script:
 - Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths that should be used.
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 - Please do not use source files that are not mentioned in this prompt.
 Please quote the Python script between one single "```Python" and "```".

  Errors in previous Attempts : {error_string}
    """
    return [f"{prompt_start}{prompt_middle}{prompt_last}"]
