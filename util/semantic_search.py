import pandas as pd
import numpy as np
import os
import pdb
from openai import OpenAI


MODEL = "text-embedding-3-large"


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def load_excel(excel_path):
    return (
        pd.read_excel(excel_path, sheet_name=0, header=1, skiprows=0, usecols=[1, 2])
        .dropna()
        .reset_index(drop=True)
    )


def get_prompt_embeddings(
    client=OpenAI(),
    excel_path="data/LLM-based data transformation results.xlsx",
    embeddings_path="data/embeddings.npy",
):
    # Load embeddings if they exist
    if os.path.exists(embeddings_path):
        return np.load(embeddings_path)

    # If the embeddings are not found, generate them
    df = load_excel(excel_path)
    prompts = df["Prompt"].tolist()
    response = client.embeddings.create(
        input=prompts,
        model=MODEL,
    )
    # Pack embeddings to a numpy array
    embeddings = np.array([r.embedding for r in response.data], dtype=np.float64)
    embeddings = np.array(embeddings)
    # Save embeddings to a file
    np.save(embeddings_path, embeddings)
    return embeddings


def get_fewshot_prompt(
    query,
    k,
    embeddings,
    client=OpenAI(),
    excel_path="data/LLM-based data transformation results.xlsx",
):

    query_embedding = (
        client.embeddings.create(
            input=query,
            model=MODEL,
        )
        .data[0]
        .embedding
    )
    query_embedding = np.array(query_embedding, dtype=np.float64)
    similarities = cosine_similarity(embeddings, query_embedding)
    # Get the top k indices
    top_k_indices = np.argsort(similarities)[::-1][:k]

    df = load_excel(excel_path)
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
        embeddings_path="../data/embeddings.npy",
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
        query, 3, embeddings, client=OpenAI(), excel_path=excel_path
    )
    pdb.set_trace()
