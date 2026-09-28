import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_35/training_4.csv", index_col=0)

# Union all source tables
df_all = pd.concat([df0, df1, df2, df3, df4], ignore_index=True)

# Group by Source Zipcode and sum Counts
df_grouped = df_all.groupby("Source Zipcode", as_index=False)["Counts"].sum()

# Ensure correct types
df_grouped["Source Zipcode"] = df_grouped["Source Zipcode"].astype(int)
df_grouped["Counts"] = df_grouped["Counts"].astype(int)

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_35/target_multisource_mcts.csv", index=False)