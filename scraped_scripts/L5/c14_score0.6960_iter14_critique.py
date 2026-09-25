import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

df = pd.merge(source2, source1, on="Ship_id")
df = pd.merge(df, source0, on="Cust_id")
df = pd.merge(df, source3, on="Prod_id")
df = pd.merge(df, source4, on="Ord_id")

# Convert IDs to integers by stripping prefixes
df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Select only the target columns
result = df[["Ship_id", "Ord_id", "Prod_id", "Cust_id"]]

# Group by all target columns to remove duplicates (no aggregation needed)
result = result.drop_duplicates(subset=["Ship_id", "Ord_id", "Prod_id", "Cust_id"])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)