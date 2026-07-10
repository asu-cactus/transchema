import pandas as pd

# Read source files
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

# Join all tables on their keys
j1 = pd.merge(s1, s2, on="Cust_id", how="inner")
j2 = pd.merge(j1, s3, on="Prod_id", how="inner")
j3 = pd.merge(j2, s4, on="Ship_id", how="inner")
j4 = pd.merge(j3, s0, on="Ord_id", how="inner")

# Select relevant columns
df = j4[["Product_Sub_Category", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()

# Aggregate by Product_Sub_Category
agg_df = df.groupby("Product_Sub_Category").agg(
    Ord_id=("Ord_id", "count"),
    Prod_id=("Prod_id", "count"),
    Ship_id=("Ship_id", "count"),
    Cust_id=("Cust_id", "count"),
    Sales=("Sales", "sum"),
    Discount=("Discount", "sum")
).reset_index()

# Convert all columns to int except Product_Sub_Category which is string
agg_df["Ord_id"] = agg_df["Ord_id"].astype(int)
agg_df["Prod_id"] = agg_df["Prod_id"].astype(int)
agg_df["Ship_id"] = agg_df["Ship_id"].astype(int)
agg_df["Cust_id"] = agg_df["Cust_id"].astype(int)
agg_df["Sales"] = agg_df["Sales"].fillna(0).astype(int)
agg_df["Discount"] = agg_df["Discount"].fillna(0).astype(int)
agg_df["Product_Sub_Category"] = agg_df["Product_Sub_Category"].astype(str)

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)