import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

# Join fact table with product dimension
r = pd.merge(s4, s0, on="Prod_id")

# Join with customer dimension
r = pd.merge(r, s1, on="Cust_id")

# Join with order dimension
r = pd.merge(r, s2, on="Ord_id")

# Join with ship dimension
r = pd.merge(r, s3, on="Ship_id")

# Select relevant columns
r = r[["Product_Sub_Category", "Order_Quantity", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

# Aggregate numeric columns by sum, group by leftmost key columns
r = r.groupby(
    ["Product_Sub_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id"],
    as_index=False
).agg({
    "Order_Quantity": "sum",
    "Sales": "sum",
    "Discount": "sum"
})

# Convert numeric columns to integer as per target schema
r["Order_Quantity"] = r["Order_Quantity"].astype(int)
r["Sales"] = r["Sales"].round().astype(int)
r["Discount"] = r["Discount"].round().astype(int)

r.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)