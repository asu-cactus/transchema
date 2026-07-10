import pandas as pd

# List all source files (assuming 3 source files for example)
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_2.csv"
]

dfs = []
for file in source_files:
    df = pd.read_csv(file, index_col=0)
    dfs.append(df)

# Union all source tables
df_all = pd.concat(dfs, ignore_index=True)

# Rename column
df_all = df_all.rename(columns={"J_CALL": "V_GENE"})

# Output
df_all.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)