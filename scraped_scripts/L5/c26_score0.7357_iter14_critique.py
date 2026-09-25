import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

# Join s1 and s2 on Ord_id
j1 = pd.merge(s1, s2, on="Ord_id", how="inner")

# Join with s4 on Prod_id
j2 = pd.merge(j1, s4, on="Prod_id", how="inner")

# Join with s0 on Ship_id
j3 = pd.merge(j2, s0, on="Ship_id", how="inner")

# Join with s3 on Cust_id
j4 = pd.merge(j3, s3, on="Cust_id", how="inner")

# Extract integer IDs from string IDs by removing prefix and converting to int
# For Ord_id, Prod_id, Ship_id, Cust_id
for col in ["Ord_id", "Prod_id", "Ship_id", "Cust_id"]:
    j4[col] = j4[col].str.extract(r'(\d+)').astype(int)

# Group by Product_Sub_Category and Order_Date
group_cols = ["Product_Sub_Category", "Order_Date"]

agg_dict = {
    "Ord_id": "min",
    "Prod_id": "min",
    "Ship_id": "min",
    "Cust_id": "min",
    "Sales": "sum"
}

result = j4.groupby(group_cols, as_index=False).agg(agg_dict)

# Convert Sales to int (since target schema Sales is integer)
result["Sales"] = result["Sales"].round().astype(int)

# Reorder columns to match target schema exactly
result = result[["Product_Sub_Category", "Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)