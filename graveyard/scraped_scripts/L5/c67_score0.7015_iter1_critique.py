import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

# Join Source5_67_0 and Source5_67_2 on Prod_id
df = pd.merge(s0, s2, on="Prod_id", how="inner")

# Join with Source5_67_1 on Ship_id
df = pd.merge(df, s1, on="Ship_id", how="inner")

# Join with Source5_67_4 on Ord_id
df = pd.merge(df, s4, on="Ord_id", how="inner")

# Join with Source5_67_3 on Cust_id
df = pd.merge(df, s3, on="Cust_id", how="inner")

# Convert IDs to int by removing prefixes
df["Ship_id"] = df["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)
df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Select target columns
result = df[["Ship_Date", "Prod_id", "Ord_id", "Ship_id", "Cust_id"]]

# Group by all columns to remove duplicates (no aggregation needed)
result = result.drop_duplicates()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)