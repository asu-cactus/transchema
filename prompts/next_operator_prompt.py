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
    all_intermediate_results: dict = {},
):
    prompt_start = f"""
    query1
    You are generating a data-pipeline to transform multiple source tables to target table and you need to answer "what operation should be performed next?". Take this decision based on "operation history", the schema of the source, target tables, and examples in the target table.
Allowed Operations: {allowed_operation_list}.
Operation History: {operation_history}

1. Target Table Name: {target_data_name}
2. Target Schema: {target_data_schema}
3. Target Examples: {target_samples}
4. Source Information: {source_information}

"""
    if not all_intermediate_results:
        prompt_middle = ""
    else:
        subprompts_middle = []
        for i, op in enumerate(operation_history):
            step = i + 1
            if step not in all_intermediate_results:
                continue
            interm = all_intermediate_results[step]
            subprompts_middle.append(
                f"After the {step}st/nd/rd/th operation {op}, the intermediate table is named 'intermediate_step{step}'.\nThe intermediate table schema is as follows: \n{interm.schema} \nExamples: {interm.source_samples_string}"
            )
        prompt_middle = "\n".join(subprompts_middle)

    prompt_last = f"""

{fd_hints}

{hints[0]}


- Please answer what operation you should perform next based on "operation history", "source tables" and "target tables" information ("schema" as well as the "examples")  in one word.
- If any two source tables have different columns, DO NOT give the UNION operation.
- If there are multiple source tables and the target table having exactly same columns, give Union operation first priority .
- If there are two source tables with different schemas that share one or a few common columns, which exist in the target data, give Join operation first priority. 
- Note that some column names, e.g., purpose, may not match the values in the column, in this case consider the column to be aggregation, e.g., count per purpose. 
- If multiple source tables share the same schema while the target table (i.e., target examples) also share the same schema, UNION must be used. However if m source tables share the same schema consisting of k non-key columns, but the target table has renamed each non-key column shared into k different columns, and thus consists of k x m non-key columns, JOIN should be applied to join all source tables on the primary key.
- If the given target examples contain duplicate keys or duplicate tuples, Group By should NOT be used.
- All source tables have to be used in all cases. For example, given target examples with schema <XXXX_NUM>, and source tables with schemas A<ROW_WID,KEYWORDS_NUM>, B<ROW_WID,XXXX_NUM>, C<ROW_WID,TECHSUPPORT_NUM>, D<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, E<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, F<ROW_WID,INTERACTIONS_NUM>, G<ROW_WID,COLLECTION_EVENTS_NUM>, H<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, I<CANCELED,ROW_WID,ACCNT_LOC,ARPU,SES,HOME_PASSED,CUST_SINCE_DT,MONTHS_AGE,CANCEL_DT,CITY,POP>, and J<ROW_WID,VISITS_NUM>, all source tables that have the same schema, such as D, E, H, and I must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, F, G, J, K on the shared attribute ROW_WID. Finally, it retrieves the attribute XXXX_NUM (this projection must be applied at the last step, otherwise the join column ROW_ID would be removed before applying the join)
- Similarly, if given target examples with schema that has all attributes <Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM>, and source tables with schemas A<ROW_WID,XXXX_NUM>, B<ROW_WID,YYYY_NUM>, C<ROW_WID,ZZZZ_NUM>, D<Attr-1, ..., Attr-K>, E<Attr-1, ..., Attr-K>, F<Attr-1, ..., Attr-K>, all source tables that have the same schema, such as C, and E must be unioned to form unioned_df. Then, unioned_df will join with A, B, C, on the shared attribute ROW_WID. Finally, it selects all attributes Attr-1, ..., Attr-K, XXXX_NUM, YYYY_NUM, ZZZZ_NUM.
- Two tables may join on columns that have different names but similar values. For example, in a source table called test_0.csv, there exists a Code column containing values such as AUS, AUT, BEL, CAN, FRA, while another source table called test_1.csv contains a column Country that has values such as FRA, BEL, GRA, USA, CAN. These source tables test_0 and test_1 can be joined on test_0.Code = test_1.Country. Similarly, if test_0 has a column Country having values Afghanistan, Albania, Algeria, Angola, etc, while test_2 has a column Host having similar country values such as France, Switzerland, United States, Germany, etc, the output of test_0 and test_1 df01 could join test_2 on df01.Country = test_2.Host. Furthermore, if test_2 contains a column Host City including values such as Paris, Bern, Albany, Berlin, and test_3 contains a column City also contains city names, they should be joined on HostCity=City.  
- Please try to make sure, using the operator history, that ALL THE COLUMNS IN THE TARGET TABLE ARE ACCOUNTED FOR.
- If you feel no more operation is needed further, please return 'NO_MORE_OPERATION'.
- You should only answer from allowed operations.
- Try not to repeat operation and it's configuration from the operation history.
- the final answer should be in $ quotes. i.e. $OPERATOR$"""
    full_prompt = f"{prompt_start}{prompt_middle}{prompt_last}"
    return [full_prompt]
