import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_3.csv", index_col=0)

# UNION all source tables (concatenate)
df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

# GROUP BY user_id and aggregate mean of sad.depressed and open.stressed
result = df_all.groupby("user_id").agg({
    "sad.depressed": "mean",
    "open.stressed": "mean"
}).reset_index()

# Rename columns to match target schema
result = result.rename(columns={
    "sad.depressed": "sad",
    "open.stressed": "stressed"
})

# Ensure correct types
result["user_id"] = result["user_id"].astype(int)
result["sad"] = result["sad"].astype(float)
result["stressed"] = result["stressed"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)