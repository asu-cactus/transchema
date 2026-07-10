import pandas as pd

# Read all source tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_39/training_4.csv", index_col=0)

# Join Source0 and Source1 on Ord_id
join_01 = pd.merge(source0, source1, on="Ord_id", how="inner")

# Join with Source2 on Ship_id
join_02 = pd.merge(join_01, source2, on="Ship_id", how="inner")

# Join with Source3 on Cust_id
join_03 = pd.merge(join_02, source3, on="Cust_id", how="inner")

# Join with Source4 on Prod_id
join_04 = pd.merge(join_03, source4, on="Prod_id", how="inner")

# Extract Product_Category and Ord_id (string columns)
# Convert Prod_id, Ship_id, Cust_id to integers by removing prefixes
join_04["Prod_id"] = join_04["Prod_id"].str.replace("Prod_", "", regex=False).astype(int)
join_04["Ship_id"] = join_04["Ship_id"].str.replace("SHP_", "", regex=False).astype(int)
join_04["Cust_id"] = join_04["Cust_id"].str.replace("Cust_", "", regex=False).astype(int)

# Group by Product_Category and Ord_id, aggregate Prod_id, Ship_id, Cust_id by min (or first)
result = join_04.groupby(["Product_Category", "Ord_id"], as_index=False).agg({
    "Prod_id": "min",
    "Ship_id": "min",
    "Cust_id": "min"
})

# Reorder columns to match target schema exactly
result = result[["Product_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id"]]

# Write to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_39/target_multisource_mcts.csv", index=False)