import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_65/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_65/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_65/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_65/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length4_65/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df = df.astype({
    'Year': str,
    'Category': str,
    'Nominee': str,
    'Movie': str,
    'Winner': str
})

# Group by all columns to remove duplicates
df_grouped = df.groupby(['Year', 'Category', 'Nominee', 'Movie', 'Winner'], as_index=False).size()

# The 'size' column is the count, but target schema does not have count column, so drop it
df_final = df_grouped.drop(columns=['size'])

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length4_65/target_multisource_mcts.csv", index=False)