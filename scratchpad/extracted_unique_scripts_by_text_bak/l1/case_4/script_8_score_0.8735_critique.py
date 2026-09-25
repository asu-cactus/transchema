import pandas as pd

# Read all source tables (assuming 4 source tables named Source1_4_0.csv ... Source1_4_3.csv)
paths = [
    "autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_4/training_3.csv"
]

dfs = [pd.read_csv(path, index_col=0) for path in paths]

# UNION all source tables
df_all = pd.concat(dfs, ignore_index=True)

# GROUP BY fname and count observations
result = df_all.groupby("fname").size().reset_index(name="count_of_obs")

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)