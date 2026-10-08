import pandas as pd

# List all source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_34/training_8.csv",
]

dfs = []
for file in source_files:
    df = pd.read_csv(file, index_col=0)
    df = df.rename(columns={"J_CALL": "V_GENE"})
    dfs.append(df)

df_union = pd.concat(dfs, ignore_index=True)

# No group by or aggregation needed, just output all rows as is
df_union.to_csv("autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv", index=False)