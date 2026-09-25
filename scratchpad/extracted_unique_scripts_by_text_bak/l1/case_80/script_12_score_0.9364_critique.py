import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_80/training_4.csv", index_col=0)

# Union all source tables
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Group by movieId and compute average rating
result = df_all.groupby("movieId", as_index=False)["rating"].mean()

# Write output with exact column names
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_80/target_multisource_mcts.csv", index=False)