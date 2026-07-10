import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_4.csv", index_col=0)

# Join Source0 and Source3 on Cust_id
joined_0 = pd.merge(source0, source3, on="Cust_id", how="inner")

# Join with Source1 on Prod_id
joined_1 = pd.merge(joined_0, source1, on="Prod_id", how="inner")

# Join with Source4 on Ord_id
joined_2 = pd.merge(joined_1, source4, on="Ord_id", how="inner")

# Select relevant columns
df = joined_2[["Product_Category", "Ship_id", "Ord_id", "Prod_id", "Cust_id", "Sales"]].copy()

# Convert string IDs to integers by removing prefixes
df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "", regex=False).astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Ship_id and Product_Category remain strings
df["Ship_id"] = df["Ship_id"].astype(str)
df["Product_Category"] = df["Product_Category"].astype(str)

# Aggregate Sales by sum after grouping by keys
df = df.groupby(
    ["Product_Category", "Ship_id", "Ord_id", "Prod_id", "Cust_id"],
    as_index=False,
    sort=False,
).agg({"Sales": "sum"})

# Round Sales and convert to int (in case of float sums)
df["Sales"] = df["Sales"].round().astype(int)

# Write output
df.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)