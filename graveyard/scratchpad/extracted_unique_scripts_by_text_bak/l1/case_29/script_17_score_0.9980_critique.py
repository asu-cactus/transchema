import pandas as pd

# Read all source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_2.csv", index_col=0)

# Union all source tables
df_union = pd.concat([df0, df1, df2], ignore_index=True)

# Group by Gender and count Purchase ID occurrences
result = df_union.groupby("Gender", as_index=False).agg({"Purchase ID": "count"}).rename(columns={"Purchase ID": "0"})

# Ensure the count column is integer type
result["0"] = result["0"].astype(int)

# Write output with exact target schema and no index
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)