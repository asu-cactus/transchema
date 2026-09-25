import pandas as pd
import re

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

# Join s1 and s4 on Ship_id
j0 = pd.merge(s1, s4, on="Ship_id", how="inner")

# Join with s3 on Cust_id
j1 = pd.merge(j0, s3, on="Cust_id", how="inner")

# Join with s2 on Ord_id
j2 = pd.merge(j1, s2, on="Ord_id", how="inner")

# Join with s0 on Prod_id
j3 = pd.merge(j2, s0, on="Prod_id", how="inner")

# Extract numeric part from IDs and convert to int
def extract_int(series):
    return series.str.extract(r'(\d+)').astype(int)

j3["Ord_id"] = extract_int(j3["Ord_id"])
j3["Prod_id"] = extract_int(j3["Prod_id"])
j3["Ship_id"] = extract_int(j3["Ship_id"])
j3["Cust_id"] = extract_int(j3["Cust_id"])

# Group by the leftmost columns that uniquely identify rows
group_cols = ["Order_Quantity", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id"]

# Aggregate Sales by sum
result = j3.groupby(group_cols, as_index=False).agg({"Sales": "sum"})

# Convert Order_Quantity and Sales to int (Sales may be float after sum)
result["Order_Quantity"] = result["Order_Quantity"].astype(int)
result["Sales"] = result["Sales"].astype(int)

# Reorder columns to match target schema exactly
result = result[["Order_Quantity", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)