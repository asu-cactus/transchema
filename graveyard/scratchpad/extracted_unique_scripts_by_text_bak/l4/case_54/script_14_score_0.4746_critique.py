import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_54/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_54/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

# Drop duplicates to get unique pairs
df_unique = df_all.drop_duplicates()

# Reorder columns to match target schema ['WhereFought', 'WarNum']
result = df_unique[['WhereFought', 'WarNum']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_54/target_multisource_mcts.csv", index=False)