import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

# Join Source2 and Source4 on Ord_id
df = pd.merge(source2, source4, on="Ord_id", how="inner")

# Join with Source1 on Ship_id
df = pd.merge(df, source1, on="Ship_id", how="inner")

# Join with Source3 on Cust_id
df = pd.merge(df, source3, on="Cust_id", how="inner")

# Join with Source0 on Prod_id
df = pd.merge(df, source0, on="Prod_id", how="inner")

# Select columns as per target schema
result = df[["Ship_Date", "Prod_id", "Ord_id", "Ship_id", "Cust_id"]].copy()

# Convert IDs to integers by stripping prefixes
result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
result["Ship_id"] = result["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)
result["Cust_id"] = result["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)