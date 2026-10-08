import pandas as pd
import glob

# List all source files matching the pattern (assuming 10 source files as per failed pipeline)
file_paths = [
    "autopipeline-benchmarks/github-pipelines/length1_65/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_65/training_9.csv",
]

dfs = [pd.read_csv(fp, index_col=0) for fp in file_paths]

df_union = pd.concat(dfs, ignore_index=True)

df_grouped = df_union.groupby("year", as_index=False).size().rename(columns={"size": "0"})

df_grouped["0"] = df_grouped["0"].astype(int)
df_grouped["year"] = df_grouped["year"].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)