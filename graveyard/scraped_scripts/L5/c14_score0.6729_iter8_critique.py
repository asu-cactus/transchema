import pandas as pd

# Read all source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

# Join Source5_14_2 with Source5_14_1 on Ship_id
df = pd.merge(df2, df1, on="Ship_id", how="inner")

# Join with Source5_14_4 on Ord_id
df = pd.merge(df, df4, on="Ord_id", how="inner")

# Join with Source5_14_3 on Prod_id
df = pd.merge(df, df3, on="Prod_id", how="inner")

# Join with Source5_14_0 on Cust_id
df = pd.merge(df, df0, on="Cust_id", how="inner")

# Convert IDs to integers by removing prefixes
df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "").astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "").astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "").astype(int)

# Select only the target columns in the correct order
target = df[["Ship_id", "Ord_id", "Prod_id", "Cust_id"]]

# Write output
target.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)