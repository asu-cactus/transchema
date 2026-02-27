def get_python_script(
    allowed_operation_list,
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    file_count,
    source_information_with_location,
    csv_save_path,
    error_string,
    all_intermediate_results,
    static_hints=False,
):
    if all_intermediate_results:
        return get_python_script_with_intermediate_materialization(
            operation_history,
            target_data_name,
            target_data_schema,
            target_samples,
            source_information_with_location,
            csv_save_path,
            error_string,
            all_intermediate_results,
        )
    elif not operation_history:
        return get_python_script_for_single_step_cot(
            target_data_name,
            target_data_schema,
            target_samples,
            source_information_with_location,
            csv_save_path,
            error_string,
        )
    else:
        return get_python_script_simple(
            operation_history,
            target_data_name,
            target_data_schema,
            target_samples,
            source_information_with_location,
            csv_save_path,
            error_string,
            static_hints,
        )


def get_python_script_simple(
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information_with_location,
    csv_save_path,
    error_string,
    static_hints=False,
):
    prompt = f"""
    You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table and STRICTLY follow the sequence of the operations mentioned in 'operation_history' list . The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way.

    Transformation Plan:

    Operation History: {operation_history}

    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}
    5. Write the result to this path {csv_save_path}

    Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths that will be used.

    Please quote the Python script between one single "```Python" and "```".
    """
    if static_hints:
        prompt += f"""
    Hints to be considered for Python code generation:
 - Your code should only take the CSV file paths given in the Source Data Information as inputs.
 - Please ensure all operation output contributed (or used) by the final output.
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
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 - Please do not use source files that are not mentioned in this prompt.
 Please quote the Python script between one single "```Python" and "```"."""
    prompt += f"""
 Errors in previous Attempts : {error_string}

    """

    return [prompt]


def get_python_script_for_single_step_cot(
    target_data_name,
    target_data_schema,
    target_samples,
    source_information_with_location,
    csv_save_path,
    error_string,
    static_hints=False,
):
    prompt = f"""You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table. The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. Before generating the code, please think step by step about the transformation plan to convert the source tables to the target table.

    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}
    5. Write the result to this path {csv_save_path}

    Based on the transformation plan, generate the Python script that implements the transformation. The script should handle data import, transformation, and export. The script should be complete and executable, not omiting any single statement. For example, please list all the source paths that will be used.

    Please quote the Python script between one single "```Python" and "```".
    """
    if static_hints:
        prompt += f"""
    Hints to be considered for Python code generation:
 - Your code should only take the CSV file paths given in the Source Data Information as inputs.
 - Please ensure all operation output contributed (or used) by the final output.
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
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 - Please do not use source files that are not mentioned in this prompt.

Hint 1:
Note that some column names, e.g., purpose, funded_year, may not match the values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case consider the column to be aggregation, e.g., count per purpose, and sum for funded_year. They should not be used in Group By columns.

Hint 2:
If the resulting data generated by the failed Python script has the same schema with the available target examples, but has more rows, it may indicate the following: (1) A Group By operator and Aggregate operators are missing. We would suggest adding a Group By operator using the left-most non-float, and unique attributes from the given target examples as GroupBy attributes and choosing the Aggregation operator such as count, average, medium, sum, etc., based on the range of valuesfor each of other columns. (2) If a Group By operator has been used, we would suggest remove some Group By attributes. (3) If OUTER join is used, it should be replaced by INNER join. (4) We shall remove rows that contain NaN values.

Hint 3:
If the resulting data generated by the failed Python script has the same schema with the available target examples, but has fewer rows, it may indicate the following: (1) If INNER join is used, it should be replaced by OUTER join. (2) We shall keep rows that contain NaN values. (3) If Group By is used, it should be removed or use more Group By attributes.


Hint 4:
If multiple source tables share the same schema while the target table (i.e., target examples) also has the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key. 

Hint 5:
Group By columns are never float types. These Group By columns correspond to columns that are UNIQUE and non-float in the target examples, which are usually at the leftmost part of the columns of the target examples.

Hint 6:
If the given target examples contain duplicate keys or duplicate rows, Group By should NOT be used. 

Hint 7:
If the average value of a column in the target examples is significantly bigger than its average values in the source tables, sum aggregation should be applied to the column, and this column should be excluded from the Group By columns. 

Hint 8:
If a column that usually has value range (such as year or funded_year) in the target table has abnormal values (e.g., 0 or 16888 for year or XXXX_year), an aggregation should be applied to the column and this column MUST be EXCLUDED from the Group By columns.

Hint 9:
JOIN is usually applied to two tables sharing the same primary key, or applied to two tables where one table has a column (i.e., foreign key) referencing to the primary key of the other table.
If many source tables have different schemas (columns), look for a dimension table that has a lot of attributes and join it with each of the rest tables (aspect tables) on shared attributes. For example, test_5.csv has columns: ,Fecha,Mes,IdAhogado,IdPersona,Localidad,Provincia,CCAA,Hora,Latitud_inc,Longitud_inc,Sexo,Edad,Nacionalidad,Origen,Extraccion,Causa,TipoAhogamiento,Factor,Intervencion,Pronostico,Localizacion,Riesgo,Reanimacion,Vigilancia,Actividad,Deteccion,ID,Estacion,Estado,Latitud_est,Longitud_est,T_med,T_max,T_min,Precipitaciones,Presion,Dir. vi.,V_Viento,Nubosidad,ProfNievecm,InsolacHoras,Distancia, test_0.csv has columns ,IdOrigen,Origen, it means test_5 may join with test_0 on Origen. Then, test_1.csv has columns ,IdPronostico,Pronostico,Mortal, so test_5 will also join with test_1 on Pronostico. Similarly, test_5 will join with test_2 (IdDeteccion,Deteccion) on Deteccion, join with test_3 (IdTipo,TipoAhogamiento) on TipoAhogamiento, join with test_4 (IdInterv,Intervencion) on Intervencion, join with test_6 (IdActividad,Actividad) on Actividad, join with test_7 (IdCausa,Causa) on Causa, and join with test_8 (IdReanima,Reanimacion) on Reanimacion.

Hint 10:
Two different tables may join on shared columns that have different names. For example, in a source table called test_0.csv, there exists a Code column containing values such as AUS, AUT, BEL, CAN, FRA, while another source table called test_1.csv contains a column Country that has values such as FRA, BEL, GRA, USA, CAN. These source tables test_0 and test_1 can be joined on test_0.Code = test_1.Country. Similarly, if test_0 has a column Country having values Afghanistan, Albania, Algeria, Angola, etc, while test_2 has a column Host having similar country values such as France, Switzerland, United States, Germany, etc, the output of test_0 and test_1 df01 could join test_2 on df01.Country = test_2.Host.

Hint 11:
All source tables have to be used in all cases. For example, given target examples with schema <XXXX_NUM>, and source tables with schemas A<ROW_WID,KEYWORDS_NUM>, B<ROW_WID,XXXX_NUM>, C<ROW_WID,TECHSUPPORT_NUM>, D<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, E<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, F<ROW_WID,INTERACTIONS_NUM>, G<ROW_WID,COLLECTION_EVENTS_NUM>, H<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, I<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, and J<ROW_WID,VISITS_NUM>, all source tables that have the same schema, such as D, E, H, and I must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, F, G, J, K on the shared attribute ROW_WID. Finally, it retrieves the attribute XXXX_NUM (this projection must be applied at the last step, otherwise the join column ROW_ID would be removed before applying the join) 
- Similarly, if given target examples with schema that has all attributes <Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM>, and source tables with schemas A<ROW_WID,XXXX_NUM>, B<ROW_WID,YYYY_NUM>, C<ROW_WID,ZZZZ_NUM>, D<Attr-1, ..., Attr-K>, E<Attr-1, ..., Attr-K>, F<Attr-1, ..., Attr-K>, all source tables that have exactly same schema, such as D and E must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, on the shared attribute ROW_WID. Finally, it selects all attributes Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM in one projection. No other processing is needed.

Hint 12:
No GROUP BY operator should be applied, if there is target examples have a single column or there is no primary key in the target examples. 

Hint 13:
IMPORTANT: NEVER use all target columns as the GROUP BY columns!!!

Hint 14:
If in the target data examples, many columns have constant values, use the same constant value in the Python script for those columns.

Hint 15: 
Consider applying string functions to certain columns that look similar but have different formats in the target and resulting data examples. 

Hint 16:
Please look at the target examples, and ensure the generated data has the same type and name for each column in the target examples.

Hint 17:
Most source files have a numerical index column, which is always the first column, and it should be ignored in the transformation. Therefore, when reading a CSV file, please add index_col=0, e.g., sourceX = pd.read_csv('autopipeline-benchmarks/github-pipelines/lengthY_Z/test_X.csv', index_col=0)


Please quote the Python script between one single "```Python" and "```".
"""
    prompt += f"""
Errors in previous Attempts : {error_string}
    """
    return [prompt]


def get_python_script_with_intermediate_materialization(
    operation_history,
    target_data_name,
    target_data_schema,
    target_samples,
    source_information_with_location,
    csv_save_path,
    error_string,
    all_intermediate_results,
    static_hints=False,
):
    # assert len(all_intermediate_results) + 1 == len(
    #   operation_history
    # ), f"len(all_intermediate_results)={len(all_intermediate_results)}, len(operation_history)={len(operation_history)}"
    past_operations = operation_history[:-1] if len(operation_history) > 1 else []
    next_operation = operation_history[-1]

    prompt_start = f"""
You are writing executable Python code at runtime. The overall goal is to convert multiple source tables to the format of the target table. Some operations have already been performed, and you need to write the code for the next operation.
The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 
    1. Target Table Name: {target_data_name}
    2. Target Schema: {target_data_schema}
    3. Target Examples: {target_samples}
    4. Source Information: {source_information_with_location}
    5. Write the result to this path {csv_save_path}

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
    prompt_last = ""
    if static_hints:
        prompt_last += f"""

    Hints to be considered for Python code generation:
 - Please write python code to execute the next operation {next_operation}. 
 - Your code should only take the CSV file paths given in the Source Data Information as inputs.
 - Please ensure all operation output contributed (or used) by the final output.
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
 - Note that each source file has a header. The first line of the csv file is a header, which should be considered before performing queries such as concat (union).
 - Please do not use source files that are not mentioned in this prompt.
"""
    prompt_last += f"""
  Errors in previous Attempts : {error_string}
    """
    return [f"{prompt_start}{prompt_middle}{prompt_last}"]
