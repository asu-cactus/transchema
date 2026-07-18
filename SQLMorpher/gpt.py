import json
import logging
import os
import time

from llm_client import LLMClient, default_tracker

# Model used for all SQLMorpher LLM calls. Set via env var so the same code
# can target OpenAI (e.g. "gpt-4-1106-preview", "gpt-4.1-mini") or a local
# Ollama model (e.g. "qwen2.5-coder:32b", "qwen3:8b", "deepseek-r1:32b",
# "mixtral:8x7b") without code changes.
SQLMORPHER_MODEL = os.environ.get("SQLMORPHER_MODEL", "gpt-4-1106-preview")

_logger = logging.getLogger(__name__)
_client = LLMClient(model=SQLMORPHER_MODEL, tracker=default_tracker, logger=_logger)


def chat_with_gpt(prompt, ifsql=True, max_tokens=4096):
    """ Interact with the configured LLM (OpenAI or Ollama) and extract the
    SQL script from the response. """
    complete_response = _client.chat(prompt, temperature=0, max_tokens=max_tokens)
    if ifsql:
        return ''.join(complete_response.split("```sql")[1].split("```")[0].strip())
    else:
        return complete_response

def _strip_sql_fence(text):
    """Extracts SQL from a (possibly partial/duplicated) markdown response.
    Handles a well-formed ```sql ... ``` block, a block missing its closing
    fence (still mid-generation), or plain unfenced SQL."""
    if "```sql" in text:
        text = text.split("```sql", 1)[1]
        if "```" in text:
            text = text.split("```", 1)[0]
        return text.strip()
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            return parts[1].strip()
    return text.strip()


def gpt4_sql_script(prompt, total_tokens, max_tokens_per_request=4096):
    start_time = time.time()
    timeout = 30
    sql_script = ""
    while len(sql_script.split()) < total_tokens:
        remaining_tokens = total_tokens - len(sql_script.split())
        tokens_to_generate = min(remaining_tokens, max_tokens_per_request)

        partial_script = chat_with_gpt(prompt, ifsql=False, max_tokens=tokens_to_generate)
        sql_script += partial_script

        # Update the prompt for the next iteration
        prompt += partial_script

        # Stop as soon as we have a complete fenced block instead of
        # continuing to badger the model until `total_tokens` "words" —
        # for smaller/local models the response is done long before that
        # word-count heuristic is satisfied, and further calls just make it
        # ramble or repeat itself.
        if "```sql" in sql_script and sql_script.count("```") >= 2:
            break

        if time.time() - start_time > timeout:
            logging.info(f"Timeout reached. Current script length:, {len(sql_script.split())}")
            logging.info(f"GPT-4 SQL PROMPT: {prompt}")
            logging.info(f"Final gpt4 sql script : {sql_script}")
            break
    return _strip_sql_fence(sql_script)


def token_usage_summary():
    """Returns the accumulated token usage / cost summary for this run."""
    return default_tracker.cost_summary()


def generate_prompt(json_file_path, template_option,output_table,output_sql,source_data_name_to_find, oneshot_data_name_to_find=None):
    # Read the JSON file
    with open(json_file_path, 'r') as file:
        data_list = json.load(file)

    # Find the item with the specified Source Data Name
    data = None
    for item in data_list:
        if item["Source Data Name"] == source_data_name_to_find:
            data = item
            break
    if data is None:
        raise ValueError(f"No data found for Source Data Name: {source_data_name_to_find}") 

    # Extract the relevant information from the JSON data
    target_data_name = data["Target Data Name"]
    target_data_schema = data["Target Data Schema"]
    source_data_name = data["Source Data Name"]
    source_data_schema = data["Source Data Schema"]
    samples = data["5 Samples of Source Data"]
    target_data_description = data["Target Data Description"]
    source_data_description = data["Source Data Description"]
    schema_change_hints = data["Schema Change Hints"]
    ground_truth = data["Ground Truth SQL"]
    
    # Find the item with the specified Oneshot Source Data Name
    if oneshot_data_name_to_find:
        if template_option < 5:
            raise ValueError("Oneshot is only supported for template option 5.")
        oneshot_data = None
        for item in data_list:
            if item["Source Data Name"] == oneshot_data_name_to_find:
                oneshot_data = item
                break
        if oneshot_data is None:
            raise ValueError(f"No data found for Oneshot Source Data Name: {oneshot_data_name_to_find}")

        # Extract the relevant information from the JSON data
        target_data_name_0 = oneshot_data["Target Data Name"]
        target_data_schema_0 = oneshot_data["Target Data Schema"]
        source_data_name_0 = oneshot_data["Source Data Name"]
        source_data_schema_0 = oneshot_data["Source Data Schema"]
        samples_0 = oneshot_data["5 Samples of Source Data"]
        target_data_description_0 = oneshot_data["Target Data Description"]
        source_data_description_0 = oneshot_data["Source Data Description"]
        schema_change_hints_0 = oneshot_data["Schema Change Hints"]
        ground_truth_0 = oneshot_data["Ground Truth SQL"]

    # Generate the prompt based on the template option
    if template_option == 1:
        prompt = f"""You are a SQL developer. Please generate a Postgres sql script to convert the first table to be consistent with the format of the second table. First, you must create the first table named {source_data_name} with only the given attributes: {source_data_schema}. Please delete the table before creating it if the first table exists. 

        Second, insert the following row(s) into the first table (treat empty value as NULL):

        {samples}

        Third, you must create a second table named {target_data_name} with only the given attributes: {target_data_schema}. Please delete the table before creating it if the first table exists.

        Finally, insert all rows from the first table into the second table, note that the selection clause in the insert statement should ignore attributes that are not needed.

        Please don't remove the first table, because we need it for validation.

        Please quote the returned SQL script between "```sql\n" and "\n```". 

        {target_data_description}"""
        
    elif template_option == 2:
        prompt = f"""You are a SQL developer. Please generate a Postgres sql script to convert the first table to be consistent with the format of the second table. First, you must create the first table named {source_data_name} with only the given attributes: {source_data_schema}. Please delete the table before creating it if the first table exists. 

        Second, insert the following row(s) into the first table and please don't remove any values (treat empty value as NULL):

        {samples}

        Third, you must create a second table named {target_data_name} with only the given attributes: {target_data_schema}. Please delete the table before creating it if the first table exists.

        Finally, insert all rows from the first table into the second table, note that the selection clause in the insert statement should ignore attributes that are not needed.

        Please don't remove the first table, because we need it for validation.

        Please quote the returned SQL script between "```sql\n" and "\n```".

        Some explanation for the first table: {source_data_description}

        Some explanation for the second table: {target_data_description}

        """
    elif template_option == 3:
        prompt = f"""You are a SQL developer. Please generate a Postgres sql script to convert the first table to be consistent with the format of the second table. First, you must create the first table named {source_data_name} with only the given attributes: {source_data_schema}. Please delete the table before creating it if the first table exists. 

        Second, insert the following row(s) into the first table and please don't remove any values (treat empty value as NULL):

        {samples}

        Third, you must create a second table named {target_data_name} with only the given attributes: {target_data_schema}. Please delete the table before creating it if the first table exists.

        Finally, insert all rows from the first table into the second table, note that the selection clause in the insert statement should ignore attributes that are not needed.

        Please don't remove the first table, because we need it for validation.

        Please quote the returned SQL script between "```sql\n" and "\n```".

        Some explanation for the first table: {source_data_description}

        Some explanation for the second table: {target_data_description}

        Some hints for the schema changes from the first table to the second table: {schema_change_hints}

        """
    elif template_option == 4:
        prompt = f"""You are a skilled Postgres SQL developer. 
        You're consulting for a tech firm working with Postgres databases. 
        Their primary focus is ensuring that time-related operations, especially those dealing with TIMESTAMP data types, are accurate and efficient.
        Let's perform some tasks:
        1. Creating the {source_data_name} Table:
        - Check if a table named {source_data_name} exists. If it does, delete it.
        - Create a new table named {source_data_name}. This table should have exact attributes from the following 
        schema: {source_data_schema}.
        - Note:{source_data_description}
        2. Populating the {source_data_name} Table:
        - Insert the provided rows (treat empty value as NULL): 
        {samples} 
        into the {source_data_name} table.
        3. Creating the {target_data_name} Table:
        - Check if a table named {target_data_name} exists. If it does, delete it.
        - Create a new table named {target_data_name}. This table should have exact attributes from the following 
        schema:{target_data_schema}.
        - Important: {target_data_description}
        4. Transforming Data from {source_data_name} to {target_data_name}:
        - Write a SQL transformation query to insert all rows from the {source_data_name} table to the {target_data_name} table.
        - Briefly explain your logic for the transformation.
        - Transformation hints: {schema_change_hints}
        Please don't remove the {source_data_name} table, because we need it for validation.
        Please quote the returned SQL script to perform these tasks between "```sql\n" and "\n```".
        Remember, accuracy and efficient handling of time data are paramount for the firm.
        """
    elif template_option == 5:
        prompt = f"""
        You are a SQL developer. Please generate a Postgres sql script to convert the first table to be consistent with the format of the second table. 
        Here is an example of the task:
        
        First, you must create the first table named {source_data_name_0} with only the given attributes: {source_data_schema_0}. Please delete the table before creating it if the first table exists. 
        Second, insert the following row(s) into the first table:
        {samples_0}
        Third, you must create a second table named {target_data_name_0} with only the given attributes: {target_data_schema_0}. Please delete the table before creating it if the first table exists.
        Finally, insert all rows from the first table into the second table, note that the selection clause in the insert statement should ignore attributes that are not needed.
        Please don't remove the first table, because we need it for validation.
        Please quote the returned SQL script between "```sql\n" and "\n```". 
        Some explanation for the first table: {source_data_description_0}
        Some explanation for the second table:  {target_data_description_0}
        
        The correct response will first insert the first table and then run the following:
        {ground_truth_0}
        
        Now, here is your task:
        
        First, you must create the first table named {source_data_name} with only the given attributes: {source_data_schema}. Please delete the table before creating it if the first table exists. 
        Second, insert the following row(s) into the first table:
        {samples}
        Third, you must create a second table named {target_data_name} with only the given attributes: {target_data_schema}. Please delete the table before creating it if the first table exists.
        Finally, insert all rows from the first table into the second table, note that the selection clause in the insert statement should ignore attributes that are not needed.
        Please don't remove the first table, because we need it for validation.
        Please quote the returned SQL script between "```sql\n" and "\n```". 
        Some explanation for the first table: {source_data_description}
        Some explanation for the second table: {target_data_description}
        """
    elif template_option == 6:
        prompt = f"""
        You are a SQL developer. Please generate a Postgres sql script to convert the first table to be consistent with the format of the second table. 
        Here is an example of the task:
        
        First, you must create the first table named {source_data_name_0} with only the given attributes: {source_data_schema_0}. Please delete the table before creating it if the first table exists. 
        Second, insert the following row(s) into the first table (treat empty value as NULL):
        {samples_0}
        Third, you must create a second table named {target_data_name_0} with only the given attributes: {target_data_schema_0}. Please delete the table before creating it if the first table exists.
        Finally, insert all rows from the first table into the second table, note that the selection clause in the insert statement should ignore attributes that are not needed.
        Please don't remove the first table, because we need it for validation.
        Please quote the returned SQL script between "```sql\n" and "\n```". 
        Some explanation for the second table:  {target_data_description_0}
        
        The correct response will first insert the first table and then run the following:
        {ground_truth_0}
        
        Now, here is your task:
        
        First, you must create the first table named {source_data_name} with only the given attributes: {source_data_schema}. Please delete the table before creating it if the first table exists. 
        Second, insert the following row(s) into the first table (treat empty value as NULL):
        {samples}
        Third, you must create a second table named {target_data_name} with only the given attributes: {target_data_schema}. Please delete the table before creating it if the first table exists.
        Finally, insert all rows from the first table into the second table, note that the selection clause in the insert statement should ignore attributes that are not needed.
        Please don't remove the first table, because we need it for validation.
        Please quote the returned SQL script between "```sql\n" and "\n```". 
        Some explanation for the second table: {target_data_description}
        """
    elif template_option == 7:
        prompt = f"""
        You are a skilled Postgres SQL developer. Please generate a Postgres sql script to convert the first table to be consistent with the format of the second table.
        
        Here is an example of the task:
        
        Please follow these steps to perform the task:
        1. Creating the {source_data_name_0} Table:
        - Check if a table named {source_data_name_0} exists. If it does, delete it.
        - Create a new table named {source_data_name_0}. This table should have exact attributes from the following 
        schema: {source_data_schema_0}.
        - Note:{source_data_description_0}
        2. Populating the {source_data_name_0} Table:
        - Insert the provided rows into the {source_data_name_0} table: \n{samples_0}\n
        3. Creating the {target_data_name_0} Table:
        - Check if a table named {target_data_name_0} exists. If it does, delete it.
        - Create a new table named {target_data_name_0}. This table should have exact attributes from the following 
        schema:{target_data_schema_0}.
        - Important: {target_data_description_0}
        4. Transforming Data from {source_data_name_0} to {target_data_name_0}:
        - Write a SQL transformation query to insert all rows from the {source_data_name_0} table to the {target_data_name_0} table.
        - Transformation hints: {schema_change_hints_0}
        Please don't remove the {source_data_name_0} table, because we need it for validation.
        Please quote the returned SQL script to perform these tasks between "```sql\n and "\n```".
        
        The correct response will first insert the first table and then run the following:
        {ground_truth_0}
        
        Now, here is your task:
        
        Please follow these steps to perform the task:
        1. Creating the {source_data_name} Table:
        - Check if a table named {source_data_name} exists. If it does, delete it.
        - Create a new table named {source_data_name}. This table should have exact attributes from the following 
        schema: {source_data_schema}.
        - Note:{source_data_description}
        2. Populating the {source_data_name} Table:
        - Insert the provided rows into the {source_data_name} table: \n{samples}\n
        3. Creating the {target_data_name} Table:
        - Check if a table named {target_data_name} exists. If it does, delete it.
        - Create a new table named {target_data_name}. This table should have exact attributes from the following 
        schema:{target_data_schema}.
        - Important: {target_data_description}
        4. Transforming Data from {source_data_name} to {target_data_name}:
        - Write a SQL transformation query to insert all rows from the {source_data_name} table to the {target_data_name} table.
        - Transformation hints: {schema_change_hints}
        Please don't remove the {source_data_name} table, because we need it for validation.
        Please quote the returned SQL script to perform these tasks between "```sql\n and "\n```".
        """
    elif template_option == 8:
        prompt = f"""
                You are a SQL developer. Please generate a Postgres sql script to convert the first table to be consistent with the format of the second table. First, you must create the first table named {target_data_name} with only the given attributes: {target_data_schema}. Please delete the table before creating it if the first table exists. 

                Second, insert the following row(s) into the first table:

                {output_table}

                Third, you must create a second table named {source_data_name} with only the given attributes: {source_data_schema}. Please delete the table before creating it if the first table exists.

                Finally, insert all rows from the first table into the second table, note that the selection clause in the insert statement should ignore attributes that are not needed.

                Please don't remove the first table, because we need it for validation.

                Please quote the returned SQL script between "```sql\n" and "\n```". 

                Some explanation for the second table:{source_data_description}
                
                If you think this transformation is impossible to achieve,please still generate a SQL code that can be executed.
                """
    elif template_option == 9:
        prompt = f"""
        SQL code:{output_sql}
        Result Table"{output_table}
        Please based on the SQL code and the result table I provided with to preform tasks below:
        1.Find the mapping(s) between the source and target schemas.The return value should be:Mapping[source_schema, target_schema].You don't need to add the Source table name and Target table name.Please quote the returned result between "```Mapping\n" and "\n```".
        2.Identify which target columns are aggregates of source columns and also the aggregation type(min,max,sum,avg).The return value should be:Aggregation[source_schema, target_schema].You don't need to add the Source table name and Target table name.Please quote the returned result between "```Agg\n" and "\n```".If there are no aggregations,please return None.
        3.Detect the operator used in the SQL script like this:Existing operator: {'group_by', 'to_char', 'max', 'min', 'sum', 'avg', 'case_statements', 'extract', 'greatest', 'least'}.Please quote the returned result between "```Operator\n" and "\n```".

        """
    else:
        raise ValueError(f"Invalid template option {template_option}.")
    print(prompt)
    #print(f"Ground Truth SQL Query: {ground_truth}")

    return prompt, ground_truth, target_data_name
