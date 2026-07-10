import pandas as pd
import re

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

# Join s4 with s2 on Ord_id
j1 = pd.merge(s4, s2, on="Ord_id", how="inner")

# Join with s0 on Prod_id
j2 = pd.merge(j1, s0, on="Prod_id", how="inner")

# Join with s1 on Cust_id
j3 = pd.merge(j2, s1, on="Cust_id", how="inner")

# Join with s3 on Ship_id
j4 = pd.merge(j3, s3, on="Ship_id", how="inner")

# Select columns as per target schema
result = j4[[
    "Product_Sub_Category",
    "Order_Quantity",
    "Ord_id",
    "Prod_id",
    "Ship_id",
    "Cust_id",
    "Sales",
    "Discount"
]].copy()

# Function to extract integer from IDs like "Ord_1082" -> 1082
def extract_int_id(s):
    # Extract digits from string
    return s.str.extract('(\d+)').astype(int)

# Convert IDs to integers
result["Ord_id"] = extract_int_id(result["Ord_id"])
result["Prod_id"] = extract_int_id(result["Prod_id"])
result["Ship_id"] = extract_int_id(result["Ship_id"])
result["Cust_id"] = extract_int_id(result["Cust_id"])

# Convert numeric columns to int
result["Order_Quantity"] = pd.to_numeric(result["Order_Quantity"], errors='coerce').fillna(0).astype(int)
result["Sales"] = pd.to_numeric(result["Sales"], errors='coerce').fillna(0).astype(int)
result["Discount"] = pd.to_numeric(result["Discount"], errors='coerce').fillna(0).astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)