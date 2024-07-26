import pandas as pd
import numpy as np
import os
import pdb
from openai import OpenAI
import tiktoken

MODEL = "text-embedding-3-small"
SHEET_NAME = ["L1-Zero-shot CoT", "L2", "L3", "L4", "L5"]


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def load_excel_ss(excel_path):
    return (
        pd.read_excel(excel_path, sheet_name=0, header=1, skiprows=0, usecols=[1, 2])
        .dropna()
        .reset_index(drop=True)
    )


def load_excel_ms(excel_path):
    df_dict = pd.read_excel(
        excel_path,
        sheet_name=SHEET_NAME,
        header=0,
        usecols=["Prompt", "Response"],
    )
    df_lens = [len(df.dropna()) for df in df_dict.values()]
    cum_lens = np.cumsum(df_lens)
    combined_df = pd.concat(df_dict.values()).dropna().reset_index(drop=True)
    return combined_df, cum_lens


def get_prompt_embeddings(
    client=OpenAI(),
    excel_path="data/LLM-based data transformation results.xlsx",
    embeddings_path="data/ms_embeddings",
    encoder=tiktoken.encoding_for_model("gpt-4"),
):
    # Load embeddings if they exist
    if os.path.exists(f"{embeddings_path}.npz"):
        return np.load(f"{embeddings_path}.npz")

    # If the embeddings are not found, generate them
    df, cum_len = load_excel_ms(excel_path)
    prompts = df["Prompt"].tolist()
    embeddings = []
    for prompt in prompts:
        # OpenAI Embedding API has a limit of 8191 tokens
        prompt = encoder.decode(encoder.encode(prompt)[:8191])
        response = client.embeddings.create(
            input=prompt,
            model=MODEL,
        )
        embeddings.append(response.data[0].embedding)
    # Pack embeddings to a numpy array
    embeddings = np.array(embeddings)
    # Save embeddings to a file
    np.savez(embeddings_path, embeddings=embeddings, cum_len=cum_len)
    return {
        "embeddings": embeddings,
        "cum_len": cum_len,
    }


def get_fewshot_prompt(
    query,
    k,
    prompt_embeddings,
    target_name,
    client=OpenAI(),
    excel_path="data/LLM-based data transformation results.xlsx",
    encoder=tiktoken.encoding_for_model("gpt-4"),
):

    # "L2" is the first set of embeddings, "L3" is the second set, etc.
    search_len = int(target_name[6:].split("_")[0]) - 1
    search_range = prompt_embeddings["cum_len"][search_len - int(SHEET_NAME[0][1])]
    embeddings = prompt_embeddings["embeddings"][:search_range]

    # Get query embedding
    # OpenAI Embedding API has a limit of 8191 tokens
    token_ids = encoder.encode(query)
    if len(token_ids) > 8191:
        token_ids = token_ids[:8191]
        # Append a warning to "log/long_queries.log"
        with open("log/long_queries.log", "a+") as f:
            f.write(f"{target_name}\n")

    query = encoder.decode(token_ids)
    query_embedding = (
        client.embeddings.create(
            input=query,
            model=MODEL,
        )
        .data[0]
        .embedding
    )
    query_embedding = np.array(query_embedding, dtype=np.float64)

    # Compute cosine similarity
    similarities = cosine_similarity(embeddings, query_embedding)
    # Get the top k indices
    top_k_indices = np.argsort(similarities)[::-1][:k]

    df, _ = load_excel_ms(excel_path)
    prompts = df["Prompt"]
    responses = df["Response"]
    examples = []
    for task_id, i in enumerate(top_k_indices):
        examples.append(
            f"""
Task {task_id + 1}:
{prompts[i]}

Response:
```Python
{responses[i]}
```\n\n"""
        )
    fewshot_prompt = "\n".join(examples)
    fewshot_prompt = f"{fewshot_prompt}\nTask {k + 1}:\n"
    return fewshot_prompt


if __name__ == "__main__":
    client = OpenAI()
    excel_path = "../data/LLM-based data transformation results.xlsx"
    embeddings = get_prompt_embeddings(
        client=client,
        excel_path=excel_path,
        embeddings_path="../data/ms_embeddings",
    )

    query = f"""
You are generating executable Python code at runtime. Please generate a Python script to convert multiple source tables to the format of the target table. The code should immediately executable in a correct way, which means it should NOT contain any placeholder for brievity. For example, even if there exists hundreds of source tables, these data needs to be loaded completely one by one or in a programmable way. 


Your Task Details:
1. Target Table Name: Target2_28
2. Target Schema: ['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score', 'School ID', 'type', 'size', 'budget']
3. Target Examples: [[0, 'Paul Bradley', 'M', '9th', 'Huang High School', 66, 79, 0, 'District', 2917, 1910635], [1, 'Victor Smith', 'M', '12th', 'Huang High School', 94, 61, 0, 'District', 2917, 1910635], [2, 'Kevin Rodriguez', 'M', '12th', 'Huang High School', 90, 60, 0, 'District', 2917, 1910635]]
4. Multi Source Information: 
Source 0:
        Source 0 Name: Source1_28_0
        Source 0 Schema: ['School ID', 'school_name', 'type', 'size', 'budget']
        Source 0 Examples: [[0, 'Huang High School', 'District', 2917, 1910635], [1, 'Figueroa High School', 'District', 2949, 1884411], [2, 'Shelton High School', 'Charter', 1761, 1056600]]
        Source 0 Path: /Users/jzou22/transchema/github-pipelines-l1/length1_28/test_0.csv
Source 1:
        Source 1 Name: Source1_28_1
        Source 1 Schema: ['Student ID', 'student_name', 'gender', 'grade', 'school_name', 'reading_score', 'math_score']
        Source 1 Examples: [[0, 'Paul Bradley', 'M', '9th', 'Huang High School', 66, 79], [1, 'Victor Smith', 'M', '12th', 'Huang High School', 94, 61], [2, 'Kevin Rodriguez', 'M', '12th', 'Huang High School', 90, 60]]
        Source 1 Path: /Users/jzou22/transchema/github-pipelines-l1/length1_28/test_1.csv

5. Write the result to this path: /Users/jzou22/transchema/github-pipelines-l1/length1_28/Target1_28_result_multi_source.csv

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

    fewshot_prompt = get_fewshot_prompt(
        query, 2, embeddings, search_len=2, client=OpenAI(), excel_path=excel_path
    )
    pdb.set_trace()
