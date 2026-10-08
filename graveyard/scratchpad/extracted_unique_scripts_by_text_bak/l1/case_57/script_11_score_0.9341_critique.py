import pandas as pd

# Read all source tables (assuming 5 source tables as per typical multi-source naming)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_57/training_4.csv", index_col=0)

# UNION all source tables
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# GROUP BY movieId and compute average rating
result = df_all.groupby("movieId", as_index=False)["rating"].mean()

# Rename columns to match target schema exactly
result.columns = ["movieId", "rating"]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_57/target_multisource_mcts.csv", index=False)