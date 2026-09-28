import pandas as pd

# Read all source tables (assuming 4 source files as per naming pattern)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_4/training_3.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY fname and count observations
result = df_all.groupby("fname").size().reset_index(name="count_of_obs")

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts.csv", index=False)