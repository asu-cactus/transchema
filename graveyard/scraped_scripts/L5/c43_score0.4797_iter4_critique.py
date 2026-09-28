import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

# Join tables on keys
j1 = pd.merge(s4, s0, on="Ord_id", how="inner")
j2 = pd.merge(j1, s1, on="Cust_id", how="inner")
j3 = pd.merge(j2, s2, on="Ship_id", how="inner")
j4 = pd.merge(j3, s3, on="Prod_id", how="inner")

# Convert ID columns to integers by extracting digits before grouping
j4["Ord_id"] = j4["Ord_id"].str.extract(r'(\d+)').astype(int)
j4["Prod_id"] = j4["Prod_id"].str.extract(r'(\d+)').astype(int)
j4["Ship_id"] = j4["Ship_id"].str.extract(r'(\d+)').astype(int)
j4["Cust_id"] = j4["Cust_id"].str.extract(r'(\d+)').astype(int)

# Group by the leftmost key columns and sum Sales
agg = j4.groupby(
    ["Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id"], as_index=False
).agg({"Sales": "sum"})

# Round Sales and convert to int
agg["Sales"] = agg["Sales"].round().astype(int)

# Select columns in target order
agg = agg[["Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

# Write output
agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)