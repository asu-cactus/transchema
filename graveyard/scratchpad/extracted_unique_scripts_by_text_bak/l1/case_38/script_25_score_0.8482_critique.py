import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_4.csv", index_col=0)

# Rename sad.depressed and open.stressed columns to distinguish after join
df0 = df0.rename(columns={"sad.depressed": "sad.depressed_0", "open.stressed": "open.stressed_0"})
df1 = df1.rename(columns={"sad.depressed": "sad.depressed_1", "open.stressed": "open.stressed_1"})
df2 = df2.rename(columns={"sad.depressed": "sad.depressed_2", "open.stressed": "open.stressed_2"})
df3 = df3.rename(columns={"sad.depressed": "sad.depressed_3", "open.stressed": "open.stressed_3"})
df4 = df4.rename(columns={"sad.depressed": "sad.depressed_4", "open.stressed": "open.stressed_4"})

# Select only needed columns to reduce memory and avoid conflicts
cols_to_keep = ["user_id", "sad.depressed_0", "open.stressed_0"]
df0 = df0[["user_id", "sad.depressed_0", "open.stressed_0"]]
df1 = df1[["user_id", "sad.depressed_1", "open.stressed_1"]]
df2 = df2[["user_id", "sad.depressed_2", "open.stressed_2"]]
df3 = df3[["user_id", "sad.depressed_3", "open.stressed_3"]]
df4 = df4[["user_id", "sad.depressed_4", "open.stressed_4"]]

# Join all dataframes on user_id
df_join = df0.merge(df1, on="user_id", how="outer") \
             .merge(df2, on="user_id", how="outer") \
             .merge(df3, on="user_id", how="outer") \
             .merge(df4, on="user_id", how="outer")

# After join, some columns may have NaN if user_id missing in some sources
# Replace NaN with 0 for aggregation (Hint 24)
df_join = df_join.fillna(0)

# Compute mean of all sad.depressed_* columns per user_id
sad_cols = [col for col in df_join.columns if col.startswith("sad.depressed")]
stressed_cols = [col for col in df_join.columns if col.startswith("open.stressed")]

# Calculate mean across all sources for sad and stressed
df_join["sad"] = df_join[sad_cols].mean(axis=1)
df_join["stressed"] = df_join[stressed_cols].mean(axis=1)

# Select final columns
result = df_join[["user_id", "sad", "stressed"]]

# Ensure correct types
result["user_id"] = result["user_id"].astype(int)
result["sad"] = result["sad"].astype(float)
result["stressed"] = result["stressed"].astype(float)

# Save to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)