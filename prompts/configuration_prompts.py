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
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what tables should be joined and at which columns?". Take this decision based on "Operation History", "Source" and "Target" (table schema as well as the examples) information.

Allowed Operations: {allowed_operation_list}.


1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Multi Source Information: {source_information}
5. Operation History: {operation_history}


-You may use the hint in your decision making process.
Hint : {hints}
{fd_hints}


- Please answer which tables should be joined and at which columns that hasn't appeared yet in "operation history".
- Usually tables will be joined on shared columns. In some popular cases, the shared column(s) is/are the primary key of each table to be joined. In some other popular cases, the shared column(s) is/are the primary key of one table to be joined and the foreign key of the other table to be joined.
- If many source tables have different schemas (columns), look for a dimension table that has a lot of attributes and join it with each of the rest tables (aspect tables) on shared attributes. For example, test_5.csv has columns: ,Fecha,Mes,IdAhogado,IdPersona,Localidad,Provincia,CCAA,Hora,Latitud_inc,Longitud_inc,Sexo,Edad,Nacionalidad,Origen,Extraccion,Causa,TipoAhogamiento,Factor,Intervencion,Pronostico,Localizacion,Riesgo,Reanimacion,Vigilancia,Actividad,Deteccion,ID,Estacion,Estado,Latitud_est,Longitud_est,T_med,T_max,T_min,Precipitaciones,Presion,Dir. vi.,V_Viento,Nubosidad,ProfNievecm,InsolacHoras,Distancia, test_0.csv has columns ,IdOrigen,Origen, it means test_5 may join with test_0 on Origen. Then, test_1.csv has columns ,IdPronostico,Pronostico,Mortal, so test_5 will also join with test_1 on Pronostico. Similarly, test_5 will join with test_2 (IdDeteccion,Deteccion) on Deteccion, join with test_3 (IdTipo,TipoAhogamiento) on TipoAhogamiento, join with test_4 (IdInterv,Intervencion) on Intervencion, join with test_6 (IdActividad,Actividad) on Actividad, join with test_7 (IdCausa,Causa) on Causa, and join with test_8 (IdReanima,Reanimacion) on Reanimacion.
- Two different tables may join on shared columns that have different names. For example, in a source table called test_0.csv, there exists a Code column containing values such as AUS, AUT, BEL, CAN, FRA, while another source table called test_1.csv contains a column Country that has values such as FRA, BEL, GRA, USA, CAN. These source tables test_0 and test_1 can be joined on test_0.Code = test_1.Country. Similarly, if test_0 has a column Country having values Afghanistan, Albania, Algeria, Angola, etc, while test_2 has a column Host having similar country values such as France, Switzerland, United States, Germany, etc, the output of test_0 and test_1 df01 could join test_2 on df01.Country = test_2.Host.
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


-You may use the hint in your decision making process.
Hint : {hints}
{fd_hints}

- Please answer on which columns "Group By" operation should be performed, on which columns aggregation should be performed and which aggregation functions should be used. 
- GroupBy columns should NEVER have float types in the given target examples. These GroupBy columns always contain UNIQUE and integer or string values in the given target examples. GroupBy columns are usually at the leftmost part of the columns of target examples.
- If a column is part of a group by operation, it will NOT be part of an aggregation operation.
- Note that some column names, e.g., purpose, funded_year, may not match the values in the column, e.g., 5 for purpose, 16844 for funded_year. In this case consider the column to be aggregation, e.g., count per purpose, and sum for funded_year. They should not be used in Group By columns.
- If many columns in the target table have similar integer values, it probably suggests a count aggregation should be used. 
- If a column (such as user_id or age) has float values (such as 1211.2234 or 33.17) in the given target examples, while having integer values (such as 1001 or 35) in the given source tables, it suggests that an "average" aggregation should be applied to the column, no matter whether the column sounds like an ID. Importantly, this column MUST BE EXCLUDED from the GroupBy columns.
- If a column that usually has value ranges (such as year or funded_year) in the target table has abnormal values (e.g., 0 or > 3000 for year or XXXX_year), an aggregation should be applied to the column. Then, this column MUST be EXCLUDED from the Group By columns. 
- If in the target data examples, many columns have similar but different numerical values such as 5 5 4 5 4, in each row, it indicates that a COUNT DISTINCT is used.
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
