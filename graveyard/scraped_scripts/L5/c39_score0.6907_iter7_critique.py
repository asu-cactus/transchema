import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

df = pd.merge(source0, source1, on="Ord_id")
df = pd.merge(df, source2, on="Ship_id")
df = pd.merge(df, source3, on="Cust_id")
df = pd.merge(df, source4, on="Prod_id")

# Convert Prod_id, Ship_id, Cust_id to integers by stripping prefixes
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
df["Ship_id"] = df["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Select only target columns
df = df[["Product_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id"]]

# Group by all target columns to remove duplicates (no aggregation)
df = df.drop_duplicates(subset=["Product_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id"])

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)