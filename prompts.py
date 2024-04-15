examples = """
Example 1:
Source Schema: {datetime, zone_16}
Target Schema: {DT_STRATA, DOW, PCT_HOURLY_0100, PCT_HOURLY_0200, PCT_HOURLY_0300, PCT_HOURLY_0400, PCT_HOURLY_0500, PCT_HOURLY_0600, PCT_HOURLY_0700, PCT_HOURLY_0800, PCT_HOURLY_0900, PCT_HOURLY_1000, PCT_HOURLY_1100, PCT_HOURLY_1200, PCT_HOURLY_1300, PCT_HOURLY_1400, PCT_HOURLY_1500, PCT_HOURLY_1600, PCT_HOURLY_1700, PCT_HOURLY_1800, PCT_HOURLY_1900, PCT_HOURLY_2000, PCT_HOURLY_2100, PCT_HOURLY_2200, PCT_HOURLY_2300, PCT_HOURLY_2400}

Source Examples: {1/1/2018 0:00 67.9}
Target Examples: {10/30/2023 1 1.020 0.960 0.960 0.940 1.000 1.100 1.210 1.230 1.150 1.120 1.160 1.080 1.030 1.030 1.050 1.050 1.080 1.170 1.220 1.370 1.410 1.350 1.220 1.030}

Thought 1: Predict the type of the source and target columns.
Action 1: TypePredict[source_examples, target_examples]
Observation 1: The predicted types for the target columns in the target_schema are as follows: DT_STRATA: DATE, DOW: INTEGER, PCT_HOURLY_0100 to PCT_HOURLY_2400: NUMERIC.

Thought 2: Find the mappings between the source and target schemas.
Action 2: Mapping[source_schema, target_schema]
Observation 2: datetime -> DT_STRATA. zone_16 -> PCT_HOURLY_0100 to PCT_HOURLY_2400.

Thought 3: Identify which target columns are aggregates of source columns.
Action 3: Aggregation[source_schema, target_schema]
Observation 3: The target columns PCT_HOURLY_0100 through PCT_HOURLY_2400 seem to be aggregates of the zone_16 values from the source schema, based on hourly intervals derived from the datetime column. The exact nature of the aggregation (e.g., sum, average) is not clear.

Thought 4: Need clarity on the aggregation type to use.
Action 4: Clarify[Which aggregation function should be used for the transformation? AVG, SUM, or another?]
Observation 4: SUM.

Thought 5: Identify if any conditions or filters need to be applied.
Action 5: Conditional[source_schema, target_schema]
Observation 5: Extract the date from datetime to populate DT_STRATA and the hour to determine which PCT_HOURLY_XXXX gets the zone_16 value. Compute the day of the week from datetime to set the DOW field. Use the hour from datetime to map zone_16 to the appropriate PCT_HOURLY_XXXX. 

Thought 6: Prepare the final transformation SQL code, including the creation of tables, data import, and exporting the results to a CSV file.
Action 6: Finish[CREATE TABLE source_table (datetime TEXT, zone_16 NUMERIC);
         COPY source_table FROM 'source_data.csv' WITH (FORMAT csv, HEADER true, NULL '');
         CREATE TABLE target_table (DT_STRATA DATE, DOW INTEGER, PCT_HOURLY_0100 NUMERIC, ..., PCT_HOURLY_2400 NUMERIC);
         INSERT INTO target_table (DT_STRATA, DOW, PCT_HOURLY_0100, ..., PCT_HOURLY_2400) SELECT DATE(datetime) AS DT_STRATA, CAST(strftime('%w', datetime) AS INTEGER) AS DOW, SUM(CASE WHEN strftime('%H', datetime) = '01' THEN zone_16 ELSE 0 END) AS PCT_HOURLY_0100, ..., SUM(CASE WHEN strftime('%H', datetime) = '00' THEN zone_16 ELSE 0 END) AS PCT_HOURLY_2400 FROM source_table GROUP BY DT_STRATA, DOW;
         COPY (SELECT * FROM target_table) TO '/path/to/your/sub_folder/target_name_result.csv' WITH CSV HEADER;]
Observation 6: The final SQL code is successfully created, including steps for table creation, data import, and exporting the results to a CSV file, tailored to map the source data to the target schema as per the identified mappings and conditions.
------------------------------------------------------------------------------------------------------------------------
"""

examples_no_clarify = """
Example 1:
Source Schema: {datetime, zone_16}
Source Examples: {1/1/2018 0:00 67.9}
Target Schema: {DT_STRATA, DOW, PCT_HOURLY_0100, PCT_HOURLY_0200, PCT_HOURLY_0300, PCT_HOURLY_0400, PCT_HOURLY_0500, PCT_HOURLY_0600, PCT_HOURLY_0700, PCT_HOURLY_0800, PCT_HOURLY_0900, PCT_HOURLY_1000, PCT_HOURLY_1100, PCT_HOURLY_1200, PCT_HOURLY_1300, PCT_HOURLY_1400, PCT_HOURLY_1500, PCT_HOURLY_1600, PCT_HOURLY_1700, PCT_HOURLY_1800, PCT_HOURLY_1900, PCT_HOURLY_2000, PCT_HOURLY_2100, PCT_HOURLY_2200, PCT_HOURLY_2300, PCT_HOURLY_2400}
Target Examples: {10/30/2023 1 1.020 0.960 0.960 0.940 1.000 1.100 1.210 1.230 1.150 1.120 1.160 1.080 1.030 1.030 1.050 1.050 1.080 1.170 1.220 1.370 1.410 1.350 1.220 1.030}

Thought 1: Predict the type of the source and target columns.
Action 1: TypePredict[source_examples, target_examples]
Observation 1: The predicted types for the target columns in the target_schema are as follows: DT_STRATA: DATE, DOW: INTEGER, PCT_HOURLY_0100 to PCT_HOURLY_2400: NUMERIC.

Thought 2: Find the mappings between the source and target schemas.
Action 2: Mapping[source_schema, target_schema]
Observation 2: datetime -> DT_STRATA. zone_16 -> PCT_HOURLY_0100 to PCT_HOURLY_2400.

Thought 3: Identify which target columns are aggregates of source columns.
Action 3: Aggregation[source_schema, target_schema]
Observation 3: The target columns PCT_HOURLY_0100 through PCT_HOURLY_2400 seem to be aggregates of the zone_16 values from the source schema, based on hourly intervals derived from the datetime column. The source schema is in minutes; thus, the aggregation function should be sum.

Thought 4: Identify if any conditions or filters need to be applied.
Action 4: Conditional[source_schema, target_schema]
Observation 4: Extract the date from datetime to populate DT_STRATA and the hour to determine which PCT_HOURLY_XXXX gets the zone_16 value. Compute the day of the week from datetime to set the DOW field. Use the hour from datetime to map zone_16 to the appropriate PCT_HOURLY_XXXX. 

Thought 5: Prepare the final transformation SQL code, including the creation of tables, data import, and exporting the results to a CSV file.
Action 5: Finish[DROP TABLE IF EXISTS source_table;
         CREATE TABLE source_table (datetime TEXT, zone_16 NUMERIC);
         COPY source_table FROM 'source_data.csv' WITH (FORMAT csv, HEADER true, NULL '');
         DROP TABLE IF EXISTS source_table;
         CREATE TABLE target_table (DT_STRATA DATE, DOW INTEGER, PCT_HOURLY_0100 NUMERIC, ..., PCT_HOURLY_2400 NUMERIC);
         INSERT INTO target_table (DT_STRATA, DOW, PCT_HOURLY_0100, ..., PCT_HOURLY_2400) SELECT DATE(datetime) AS DT_STRATA, CAST(strftime('%w', datetime) AS INTEGER) AS DOW, SUM(CASE WHEN strftime('%H', datetime) = '01' THEN zone_16 ELSE 0 END) AS PCT_HOURLY_0100, ..., SUM(CASE WHEN strftime('%H', datetime) = '00' THEN zone_16 ELSE 0 END) AS PCT_HOURLY_2400 FROM source_table GROUP BY DT_STRATA, DOW;
         COPY (SELECT * FROM target_table) TO '/path/to/your/sub_folder/target_name_result.csv' WITH CSV HEADER;]
Observation 5: DROP TABLE IF EXISTS source_table;
         CREATE TABLE source_table (datetime TEXT, zone_16 NUMERIC);
         COPY source_table FROM 'source_data.csv' WITH (FORMAT csv, HEADER true, NULL '');
         DROP TABLE IF EXISTS source_table;
         CREATE TABLE target_table (DT_STRATA DATE, DOW INTEGER, PCT_HOURLY_0100 NUMERIC, ..., PCT_HOURLY_2400 NUMERIC);
         INSERT INTO target_table (DT_STRATA, DOW, PCT_HOURLY_0100, ..., PCT_HOURLY_2400) SELECT DATE(datetime) AS DT_STRATA, CAST(strftime('%w', datetime) AS INTEGER) AS DOW, SUM(CASE WHEN strftime('%H', datetime) = '01' THEN zone_16 ELSE 0 END) AS PCT_HOURLY_0100, ..., SUM(CASE WHEN strftime('%H', datetime) = '00' THEN zone_16 ELSE 0 END) AS PCT_HOURLY_2400 FROM source_table GROUP BY DT_STRATA, DOW;
         COPY (SELECT * FROM target_table) TO '/path/to/your/sub_folder/target_name_result.csv' WITH CSV HEADER;
------------------------------------------------------------------------------------------------------------------------
"""
'''
type_predict_template = """
You are a Postgres SQL developer. Given the source schema '{source_schema}', target schema '{target_schema}', source data examples {source_examples}, and target data examples {target_examples}, your task is to determine the data types for each field in these schemas based exclusively on the formats present in the provided data samples.

Examine each field in the source and target schemas and their corresponding sample values. Base your data type predictions solely on the observed formats in these samples. For example, if a numeric field in the samples contains decimal points (e.g., '2.0'), classify it as DECIMAL or FLOAT, even if the context might typically suggest an INTEGER.

Provide a summary of the predicted data types for each field, ensuring your predictions reflect the data formats exactly as they appear in the samples, with no contextual assumptions.

Enclose your final data type predictions within [START] and [END] markers for clarity.
"""
'''
type_predict_template = """
You are a Postgres SQL developer. Given the source schema '{source_schema}', target schema '{target_schema}', source data examples {source_examples}, and target data examples {target_examples}, your task is to determine the data types for each field in these schemas. Your analysis should be based exclusively on the formats present in the provided data samples.

Carefully examine each field in the source and target schemas alongside their corresponding sample values. Base your data type predictions on the observed formats in these samples. For instance, if a date field in the samples is in the format 'DD/MM/YYYY', classify it as TEXT to maintain the format. For a numeric field with decimal points (e.g., '2.0'), classify it as DECIMAL or FLOAT. Do not make predictions based on typical context or standard practices but strictly on the data format present in the examples.

Provide a detailed summary of the predicted data types for each field. Ensure that your predictions align precisely with the formats as they appear in the samples, with emphasis on accurate format representation.

Enclose your final data type predictions within [START] and [END] markers for clarity. This summary should serve as a clear and precise guide for setting up the database schema according to the specific needs dictated by the data's format.
"""

column_mapping_template = """
You are a Postgres SQL developer. Given source_schema: {source_schema}, target_schema: {target_schema}, identify mappings. Execute your analysis step by step. Once complete, provide a concise summary of the mappings. Wrap the final concise answer between [START] and [END]
"""

aggregation_template = """
You are a Postgres SQL developer. Given the source_schema: '{source_schema}', target_schema: '{target_schema}', source data examples: '{source_examples}', and target data examples: '{target_examples}', analyze these details to predict which target columns are aggregates of source columns.

Review the relationships between the fields in the source and target schemas, informed by the data examples. Identify and hypothesize where a target column might be an aggregate of one or more source columns, such as sums, counts, averages, or other aggregate functions. Base your prediction on the patterns observed in the data samples.

Provide a direct and concise summary of your predictions about the aggregations. 

Enclose your final aggregation predictions within [START] and [END] markers for clarity."""

agg_func_detect_template = """
Given the previous analysis on schema transformation {agg_analysis}, please review the provided details to determine the presence and type of any SQL aggregation function suggested. The analysis aimed to identify if target columns are aggregates of source columns, using functions like SUM, COUNT, AVERAGE, MAX, MIN, or other SQL aggregate functions based on the patterns observed in the source and target data examples.

Perform the following steps in your response:

1. Identify whether an SQL aggregation function was suggested in the analysis. If a specific function (e.g., SUM, COUNT, AVERAGE) was mentioned or implied, please name the function in uppercase letters.

2. If the analysis implies or suggests an aggregation operation without specifying a function, describe the operation briefly (e.g., "total sales suggesting SUM").

3. If no aggregation function or operation was suggested, and it seems no aggregation is necessary for the transformation, simply state "NO AGGREGATION".

Format your response succinctly for easy extraction, using the following template:

[START] 
- Aggregation Function Identified: [Function Name/Operation Description/NO AGGREGATION]
[END]

Ensure your response directly addresses the analysis outcome, focusing on the aggregation function or the lack thereof.
"""

gen_new_agg_func_template = """
Given the detailed context of a schema transformation task, including the source and target schemas, as well as examples of the source and target data, we are seeking an alternative SQL aggregation function that differs from those previously identified. The details are as follows:

- Source Schema: '{source_schema}'
- Target Schema: '{target_schema}'
- Source Data Examples: '{source_examples}'
- Target Data Examples: '{target_examples}'

Previously identified aggregation functions include: {list_of_prev_agg_funcs}.

With this context in mind, your task is to suggest a logical alternative SQL aggregation function that is different from the previously listed ones. This alternative should also be applicable for achieving the transformation from the source schema to the target schema, considering the data patterns and relationships between the source and target schemas.

Please provide:
1. The name of an alternative SQL aggregation function (e.g., "MAX", "MIN", if not already listed).
2. A brief explanation of why this function is a viable alternative, given the provided schemas and data examples.

Make sure your suggestion is distinct from the previously identified functions.

[START] Your alternative aggregation function suggestion here. [END]
"""

conditional_template = """
You are a Postgres SQL developer. Given source_schema: {source_schema}, target_schema: {target_schema}, identify any conditions or filters that need to be applied. Execute your analysis step by step. Once complete, provide a concise summary of the conditional dependencies. Wrap the final concise answer between [START] and [END]
"""

finish_template = """
You are a Postgres SQL developer. Given the prompt: {prompt}, provide the final SQL code for the transformation. Ensure the SQL syntax is correct. Comment out any SQL that will cause syntax errors. Wrap the final SQL code between [START] and [END]
"""

init_template = """Welcome to the SQL Schema Transformation Task. Your mission is to transform a given source schema into a target schema. This task requires not only technical precision but also thoughtful consideration of the data and its context, utilizing AI-assisted tools effectively.

Essential Tools at Your Disposal:
- TypePredict: Predicts the datatype for columns, ensuring data type alignment. [Parameters: source_column_examples, target_column_examples].
- Mapping: Establishes correspondences between source and target schema columns, crucial for schema alignment. [Parameters: source_schema, target_schema].
- Aggregation (Enhanced Analysis): Determines if target columns are aggregates of source columns and suggests the types of aggregation that make sense given the data context. For example, with 'dt' in the source and 'avg temp' in the target, the tool should infer the likelihood of an 'average over time' aggregation. [Parameters: source_schema, target_schema].
- Conditional: Identifies conditions or filters necessary for the transformation, key for customizing data processing. [Parameters: source_schema, target_schema, condition].
- Finish: Finalizes the task with the transformation SQL code, central to completing the process. [Parameters: transformation_sql_code].

Selective Tool:
- Clarify: To be used judiciously to resolve specific ambiguities or seek essential information, avoiding overuse. [Parameters: query].

Example for Guidance: {examples}

Your Task Details:
1. Source Schema: {source_schema}
2. Source Table Name: {source_name}
3. Target Schema: {target_schema}
4. Target Table Name: {target_name}
5. Source Examples: {source_examples}
6. Target Examples: {target_examples}
7. Data File Path: {test_0_path}.

You must conclude with the 'Finish' tool to generate the final transformation SQL code.

Transformation SQL Code Steps:
1. Employ all essential tools for a comprehensive analysis and accurate transformation of data, with a special focus on thoughtful aggregation analysis.
2. Create Source Table: Define and create the source table '{source_name}', dropping it first if it exists.
3. Data Import: Load data from CSV at '{test_0_path}', treating empty values as NULL.
4. Create Target Table: Define and create the target table '{target_name}', dropping it first if it exists.
5. COPY the SQL result into a CSV file "{result_path}{target_name}_result.csv".

Ensure the 'transformation_sql_code' incorporates insights from all tools, especially the enhanced aggregation analysis, tailored to the specific requirements of the given schemas and data paths.

"""
'''
init_template_no_clarify = """
Perform a SQL schema transformation task with interleaved Thought, Action, Observation steps. Given the source and target schemas, provide a transformation strategy and relevant SQL operations. Use the following actions/tools:

Essential Actions at Your Disposal:
- TypePredict (Robust Decision-Making): Predicts the datatype for columns, bearing in mind the subset nature of the provided source data. Given the potential for unseen decimal values in the complete dataset, default to 'DECIMAL' for numerical columns unless there is absolute certainty that the data is strictly integers. This approach is to preempt and prevent type mismatch errors in the full dataset. [Parameters: source_column_examples, target_column_examples].
- Mapping: Establishes correspondences between source and target schema columns. Ensure to use double quotes for any reserved keywords used as column names, such as "user". [Parameters: source_schema, target_schema].
- Aggregation (Contextual Analysis): Determines if target columns are aggregates of source columns and infers the types of aggregation appropriate for the data context. [Parameters: source_schema, target_schema].
- Conditional: Identifies conditions or filters for the transformation. [Parameters: source_schema, target_schema, condition].

Mandatory Final Action:
- Finish: This is the conclusive step. Execute "Finish[transformation_sql_code]" with the final SQL code for the transformation. This action signifies the end of the task processing. [Parameters: transformation_sql_code].

Example for Guidance: {examples}

Your Task Details:
1. Source Schema: {source_schema}
2. Source Table Name: {source_name}
3. Target Schema: {target_schema}
4. Target Table Name: {target_name}
5. Source Examples: {source_examples}
6. Target Examples: {target_examples}
7. Data File Path: {test_0_path}.

The task concludes with the "Finish[transformation_sql_code]" action.
In the mandatory final action: "Finish[transformation_sql_code]" with your finalized transformation SQL code. This step marks the completion of the task.
The 'transformation_sql_code' is a placeholder and must be replaced with the actual transformation SQL code. The code must incorporate insights from all tools, especially the aggregation analysis, and be tailored to the specific schemas and data paths. 

In the Finish action, follow and only use the following steps to generate the 'transformation_sql_code'; ensure the syntax correctness of the code, do not use 'Finish' in transformation_sql_code:
1. Analyze using all tools for a comprehensive understanding and accurate data transformation.
2. Create Source Table: Define and create the source table '{source_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names. Ensure proper handling of inferred date formats from the examples.
3. Data Import: Load data from CSV at '{test_0_path}', treating empty values as NULL.
4. Create Target Table: Define and create the target table '{target_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names. Ensure proper handling of inferred date formats from the examples.
5. COPY the SQL result into a CSV file "{result_path}{target_name}_result.csv".
"""
'''
init_template_no_clarify = """
Perform a SQL schema transformation task with interleaved Thought, Action, Observation steps. Given the source and target schemas, provide a transformation strategy and relevant SQL operations. Use the following actions/tools:

Essential Actions at Your Disposal:
- TypePredict (Robust Decision-Making): Predicts the datatype for columns, bearing in mind the subset nature of the provided source data. Given the potential for unseen decimal values in the complete dataset, default to 'DECIMAL' for numerical columns unless there is absolute certainty that the data is strictly integers. For date columns, carefully consider whether to use 'DATE' or 'TEXT' based on the format and usage requirements. [Parameters: source_column_examples, target_column_examples].
- Mapping: Establishes correspondences between source and target schema columns. Ensure to use double quotes for any reserved keywords used as column names, such as "user". Include strategies for handling date formats in this process. [Parameters: source_schema, target_schema].
- Aggregation (Contextual Analysis): Determines if target columns are aggregates of source columns and infers the types of aggregation appropriate for the data context. Pay special attention to date fields and how their format might impact aggregation. [Parameters: source_schema, target_schema].
- Conditional: Identifies conditions or filters for the transformation, including any related to date formats. [Parameters: source_schema, target_schema, condition].

Mandatory Final Action:
- Finish: This is the conclusive step. Execute "Finish[transformation_sql_code]" with the final SQL code for the transformation. Ensure this code accounts for the handling of date formats, whether preserving them as 'TEXT' or converting them to 'DATE', and addresses any syntax issues. [Parameters: transformation_sql_code].

Example for Guidance: {examples}

Your Task Details:
1. Source Schema: {source_schema}
2. Source Table Name: {source_name}
3. Target Schema: {target_schema}
4. Target Table Name: {target_name}
5. Source Examples: {source_examples}
6. Target Examples: {target_examples}
7. Data File Path: {test_0_path}.

The task concludes with the "Finish[transformation_sql_code]" action.
In the mandatory final action: "Finish[transformation_sql_code]" with your finalized transformation SQL code. This step marks the completion of the task.
The 'transformation_sql_code' is a placeholder and must be replaced with the actual transformation SQL code. The code must incorporate insights from all tools, especially the aggregation analysis, and be tailored to the specific schemas and data paths, with a particular focus on the correct handling of date formats.

In the Finish action, follow and only use the following steps to generate the 'transformation_sql_code'; ensure the syntax correctness of the code, including the handling of date formats:
1. Analyze using all tools for a comprehensive understanding and accurate data transformation.
2. Create Source Table: Define and create the source table '{source_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names and carefully handle date formats as per the analysis.
3. Data Import: Load data from CSV at '{test_0_path}', treating empty values as NULL and correctly handling date formats.
4. Create Target Table: Define and create the target table '{target_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names and ensure date formats are correctly handled.
5. COPY the SQL result into a CSV file "{result_path}{target_name}_result.csv".
"""

baseline_examples = """
Example 1:
Source Schema: {datetime, zone_16}
Source Examples: {1/1/2018 0:00 67.9}
Target Schema: {DT_STRATA, DOW, PCT_HOURLY_0100, PCT_HOURLY_0200, PCT_HOURLY_0300, PCT_HOURLY_0400, PCT_HOURLY_0500, PCT_HOURLY_0600, PCT_HOURLY_0700, PCT_HOURLY_0800, PCT_HOURLY_0900, PCT_HOURLY_1000, PCT_HOURLY_1100, PCT_HOURLY_1200, PCT_HOURLY_1300, PCT_HOURLY_1400, PCT_HOURLY_1500, PCT_HOURLY_1600, PCT_HOURLY_1700, PCT_HOURLY_1800, PCT_HOURLY_1900, PCT_HOURLY_2000, PCT_HOURLY_2100, PCT_HOURLY_2200, PCT_HOURLY_2300, PCT_HOURLY_2400}
Target Examples: {10/30/2023 1 1.020 0.960 0.960 0.940 1.000 1.100 1.210 1.230 1.150 1.120 1.160 1.080 1.030 1.030 1.050 1.050 1.080 1.170 1.220 1.370 1.410 1.350 1.220 1.030}

The predicted types for the target columns in the target_schema are as follows: DT_STRATA: DATE, DOW: INTEGER, PCT_HOURLY_0100 to PCT_HOURLY_2400: NUMERIC.

Mappings between the source and target schemas are as follows: datetime -> DT_STRATA. zone_16 -> PCT_HOURLY_0100 to PCT_HOURLY_2400.

The target columns PCT_HOURLY_0100 through PCT_HOURLY_2400 seem to be aggregates of the zone_16 values from the source schema, based on hourly intervals derived from the datetime column. The source schema is in minutes; thus, the aggregation function should be sum.

Extract the date from datetime to populate DT_STRATA and the hour to determine which PCT_HOURLY_XXXX gets the zone_16 value. Compute the day of the week from datetime to set the DOW field. Use the hour from datetime to map zone_16 to the appropriate PCT_HOURLY_XXXX. 

The final transformation SQL code is

```sql
CREATE TABLE source_table (datetime TEXT, zone_16 NUMERIC);
COPY source_table FROM 'source_data.csv' WITH (FORMAT csv, HEADER true, NULL '');
CREATE TABLE target_table (DT_STRATA DATE, DOW INTEGER, PCT_HOURLY_0100 NUMERIC, ..., PCT_HOURLY_2400 NUMERIC);
INSERT INTO target_table (DT_STRATA, DOW, PCT_HOURLY_0100, ..., PCT_HOURLY_2400) SELECT DATE(datetime) AS DT_STRATA, CAST(strftime('%w', datetime) AS INTEGER) AS DOW, SUM(CASE WHEN strftime('%H', datetime) = '01' THEN zone_16 ELSE 0 END) AS PCT_HOURLY_0100, ..., SUM(CASE WHEN strftime('%H', datetime) = '00' THEN zone_16 ELSE 0 END) AS PCT_HOURLY_2400 FROM source_table GROUP BY DT_STRATA, DOW;
COPY (SELECT * FROM target_table) TO '/path/to/your/sub_folder/target_name_result_monolithic.csv' WITH CSV HEADER;
```
"""

monolithic_template = """
You are a SQL developer. Please generate a Postgres sql script to convert the source table to be consistent with the format of the target table.

Your Task Details:
1. Source Schema: {source_schema}
2. Source Table Name: {source_name}
3. Target Schema: {target_schema}
4. Target Table Name: {target_name}
5. Source Examples: {source_examples}
6. Target Examples: {target_examples}
7. Data File Path: {test_0_path}.

Do the following analytical steps:
- TypePredict (Robust Decision-Making): Predicts the datatype for columns, bearing in mind the subset nature of the provided source data. Given the potential for unseen decimal values in the complete dataset, default to 'DECIMAL' for numerical columns unless there is absolute certainty that the data is strictly integers. For date columns, carefully consider whether to use 'DATE' or 'TEXT' based on the format and usage requirements. [Parameters: source_column_examples, target_column_examples].
- Mapping: Establishes correspondences between source and target schema columns. Ensure to use double quotes for any reserved keywords used as column names, such as "user". Include strategies for handling date formats in this process. [Parameters: source_schema, target_schema].
- Aggregation (Contextual Analysis): Determines if target columns are aggregates of source columns and infers the types of aggregation appropriate for the data context. Pay special attention to date fields and how their format might impact aggregation. [Parameters: source_schema, target_schema].
- Conditional: Identifies conditions or filters for the transformation, including any related to date formats. [Parameters: source_schema, target_schema, condition].

Generate SQL code for the transformation. Ensure this code accounts for the handling of date formats, whether preserving them as 'TEXT' or converting them to 'DATE', and addresses any syntax issues. [Parameters: transformation_sql_code].
1. Analyze using all tools for a comprehensive understanding and accurate data transformation.
2. Create Source Table: Define and create the source table '{source_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names and carefully handle date formats as per the analysis.
3. Data Import: Load data from CSV at '{test_0_path}', treating empty values as NULL and correctly handling date formats.
4. Create Target Table: Define and create the target table '{target_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names and ensure date formats are correctly handled.
5. COPY the SQL result into a CSV file "{result_path}{target_name}_result_monolithic.csv".

Ensure the generated sql code incorporates insights from the analytical steps, especially the enhanced aggregation analysis, tailored to the specific requirements of the given schemas and data paths.

Ensure the 'COPY' command is used for both data import and export steps. Do not comment them out as PostgreSQL support direct file writes from queries. Please quote the returned SQL script between "```sql\n" and "\n```"
"""

monolithic_template_join = """
You are a SQL developer. Please generate a Postgres sql script to convert multi source table to be consistent with the format of the target table(Join or Union).

Your Task Details:
1. Multi Source Schema: {source_schema}
2. Multi Source Table Name: {source_name}
3. Target Schema: {target_schema}
4. Target Table Name: {target_name}
5. Multi Source Examples: {source_examples}
6. Target Examples: {target_examples}
7. Multi Source Data File Path: {test_0_path}.

Do the following analytical steps:
- TypePredict (Robust Decision-Making): Predicts the datatype for columns, bearing in mind the subset nature of the provided source data. Given the potential for unseen decimal values in the complete dataset, default to 'DECIMAL' for numerical columns unless there is absolute certainty that the data is strictly integers. For date columns, carefully consider whether to use 'DATE' or 'TEXT' based on the format and usage requirements. [Parameters: source_column_examples, target_column_examples].
- Mapping: Establishes correspondences between source and target schema columns. Ensure to use double quotes for any reserved keywords used as column names, such as "user". Include strategies for handling date formats in this process. [Parameters: source_schema, target_schema].
- Aggregation (Contextual Analysis): Determines if target columns are aggregates of source columns and infers the types of aggregation appropriate for the data context. Pay special attention to date fields and how their format might impact aggregation. [Parameters: source_schema, target_schema].
- Conditional: Identifies conditions or filters for the transformation, including any related to date formats. [Parameters: source_schema, target_schema, condition].
- Join or Union: Determine the appropriate method for combining the multiple source tables, ensuring that the resulting data is consistent with the target schema. [Parameters: source_schema, target_schema].

Generate SQL code for the transformation. Ensure this code accounts for the handling of date formats, whether preserving them as 'TEXT' or converting them to 'DATE', and addresses any syntax issues. [Parameters: transformation_sql_code].
1. Analyze using all tools for a comprehensive understanding and accurate data transformation.
2. Create Source Table: Define and create the source table '{source_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names and carefully handle date formats as per the analysis.
3. Data Import: Load data from CSV at '{test_0_path}', treating empty values as NULL and correctly handling date formats.
4. Create Target Table: Define and create the target table '{target_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names and ensure date formats are correctly handled.
5. COPY the SQL result into a CSV file "{result_path}{target_name}_result_monolithic.csv".

Ensure the generated sql code incorporates insights from the analytical steps, especially the enhanced aggregation analysis, tailored to the specific requirements of the given schemas and data paths.

Please join on track_id.

Ensure the 'COPY' command is used for both data import and export steps. Do not comment them out as PostgreSQL support direct file writes from queries. Please quote the returned SQL script between "```sql\n" and "\n```"


"""

cot_multi_source_template = """
You are a SQL developer. Please generate a Postgres sql script to convert multi source table to be consistent with the format of the target table (Consider Join or Union).

Your Task Details:
1. Target Table Name: {target_name}
2. Target Schema: {target_schema}
3. Target Examples: {target_examples}
4. Multi Source Information: {source_info}

Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.

Transformation Plan:
- Provide a high-level plan for transforming the data from the source tables to match the target table format. 
Transformation Plan:
- Provide a detailed plan, step by step for transforming the data from the source tables to match the target table format. 
- Each step should be a concrete data manipulation, such as a query.
- Each step could be something similar to the following candidate steps:
(1) union two tables that have similar schemas
(2) join two tables that have shared columns on the shared columns
(3) aggregation
(4) selection or filtering
(5) applying a projection or transformation function.

SQL Script:
Based on the transformation plan, generate the SQL script that implements the transformation. Ensure this code accounts for the handling of date formats, whether preserving them as 'TEXT' or converting them to 'DATE', and addresses any syntax issues. [Parameters: transformation_sql_code].
The script should handle table creation, data import, transformation, and export:
- Create Source Table: Define and create the source tables. For each source table, dropping it first if it exists. Use double quotes for any reserved keywords used as column names and carefully handle date formats as per the analysis.
- Data Import: Load data from CSV at '{test_0_path}', treating empty values as NULL and correctly handling date formats.
- Create Target Table: Define and create the target table '{target_name}', dropping it first if it exists. Use double quotes for any reserved keywords used as column names and ensure date formats are correctly handled.
- COPY the SQL result into a CSV file "{result_path}{target_name}_result_cot_multi_source.csv".

Do not omit any necessary steps (even if there are repetitions) in the transformation process. Always ensure that the SQL script is complete and accurate, reflecting the specific requirements of the given schemas and data paths.
Never skip any step for brevity, as each step is crucial for the successful transformation of the data.
Never skip Data import steps, as they are essential for the transformation process.
Ensure the 'COPY' command is used for both data import and export steps. Do not comment the COPY out. 
Please quote the returned SQL script between "```sql\n" and "\n```"
"""

cot_multi_source_python_template = """
You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table. The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 


Your Task Details:
1. Target Table Name: {target_name}
2. Target Schema: {target_schema}
3. Target Examples: {target_examples}
4. Multi Source Information: {source_info}
5. Write the result to this path: {result_path}

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
Please quote the Python script between "```Python" and "```"
- If source tables have simialr schema and dissimilar keys, we shall use union (concat)
- If source tables have similar schema and similar keys, we shall use join (in most cases, inner join rather than outer join should be used)

"""
# You are a data administrator. You are very good at performing data schema transformation tasks.
# You are given source schemas and a target schema and some example data. You are asked to transform the source schema to the target schema.
# In addition to answering the question, you are also expected to provide a step-by-step explanation of the answer.
# In your reponse, try to use SQL or Python code to demonstrate the transformation steps.

cot_template = """
You are a SQL developer tasked with transforming data from a source table to match the format of a target table in a Postgres database. Please generate the steps and the corresponding SQL script for this transformation. 

Task Details:
1. Source Schema: {source_schema}
2. Source Table Name: {source_name}
3. Target Schema: {target_schema}
4. Target Table Name: {target_name}
5. Source Examples: {source_examples}
6. Target Examples: {target_examples}
7. Data File Path: {test_0_path}.

Note: The row examples provided are not necessarily corresponding rows. They are simply examples of rows in the source and target schemas.

Steps for Transformation:
1. Analyze the source and target table schemas and examples to identify differences in column names, data types, and formats, particularly focusing on how date formats are handled.
2. Create the source table '{source_name}' using the '{source_schema}' schema, ensuring to drop it first if it exists. Use double quotes for any reserved keywords used as column names. Pay special attention to handling date formats as per the analysis in step 1.
3. Import data from the CSV file located at '{test_0_path}' into the source table, treating empty values as NULL and correctly handling date formats.
4. Create the target table '{target_name}' using the '{target_schema}' schema, ensuring to drop it first if it exists. Use double quotes for any reserved keywords used as column names. Ensure that the data types and formats, especially for dates, match the target schema.
5. Transform and insert data from the source table into the target table. Detail the steps involved in this process.
6. Export the transformed data from the target table into a CSV file named "{result_path}{target_name}_result_cot.csv" using the 'COPY' command.

Please generate the SQL script that implements these steps. Ensure the 'COPY' command is used for both data import and export steps. The SQL script should be quoted between "```sql\n" and "\n```".
"""


ultimate_task = 'Output the SQL code for the transformation.'

actions = ["TypePredict", "DirectMapping", "Aggregation", "Clarify", "Conditional", "Finish"]

treatment_abbreviations_template = """Transform detailed medical treatment regimens into their abbreviated forms. The goal is to simplify complex treatment descriptions for easier analysis and comparison."
Transformation Rules:

"Use acronyms or the first letter(s) of each drug's name to create abbreviations."
"Concatenate multiple treatments with a '+' sign."
"Use well-known abbreviations for common treatment types (e.g., ADT for androgen deprivation therapy)."
"Exclude supportive treatments unless they are a primary component of the therapy."
Example Shots:

Original: "Docetaxel 6 cycles at 75mg/m²/cycle, one cycle every 3 weeks; Standard androgen deprivation"
Abbreviated: "Docetaxel + ADT"

Original: "Enzalutamide 160mg OD; Abiraterone acetate 1000mg OD + Prednisolone 5mg BID; Standard androgen deprivation"
Abbreviated: "Enzalutamide + Abiraterone + ADT"

Original: "Darolutamide 600mg BID; Docetaxel 6 cycles at 75mg/m²/cycle, one cycle every 3 weeks; Standard androgen deprivation"
Abbreviated: "DARO + D + ADT"

Instructions:

("Based on these examples, create abbreviations for the following treatment regimens (provide new examples)."
"""
