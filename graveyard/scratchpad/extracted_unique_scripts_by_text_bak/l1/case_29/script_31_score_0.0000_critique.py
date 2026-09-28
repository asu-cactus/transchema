import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_29/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Normalize Gender column: strip whitespace and unify case
df['Gender'] = df['Gender'].str.strip()

# Map gender values to target categories dynamically
def map_gender(g):
    g_lower = g.lower()
    if g_lower == 'female':
        return 'Female'
    elif g_lower == 'male':
        return 'Male'
    else:
        return 'Other / Non-Disclosed'

df['Gender'] = df['Gender'].apply(map_gender)

# Group by Gender and count Purchase ID
result = df.groupby('Gender').agg({'Purchase ID': 'count'}).reset_index()

# Rename count column to '0' as in target schema
result = result.rename(columns={'Purchase ID': '0'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)