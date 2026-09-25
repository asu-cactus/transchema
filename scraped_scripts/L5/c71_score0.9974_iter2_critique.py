import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

# Join source0 and source1 on Cust_id
join_01 = pd.merge(source0, source1, on="Cust_id", how="inner")

# Join with source2 on Ship_id
join_012 = pd.merge(join_01, source2, on="Ship_id", how="inner")

# Join with source4 on Ord_id
join_0124 = pd.merge(join_012, source4, on="Ord_id", how="inner")

# Group by Order_Priority and Ship_Mode, aggregate counts of other columns
grouped = join_0124.groupby(["Order_Priority", "Ship_Mode"], as_index=False).agg({
    "Ord_id": "count",
    "Prod_id": "count",
    "Ship_id": "count",
    "Cust_id": "count",
    "Sales": "count",
    "Discount": "count"
})

# Rename columns to match target schema exactly
result = grouped.rename(columns={
    "Ord_id": "Ord_id",
    "Prod_id": "Prod_id",
    "Ship_id": "Ship_id",
    "Cust_id": "Cust_id",
    "Sales": "Sales",
    "Discount": "Discount"
})

# Convert all columns to int (they are counts)
result["Ord_id"] = result["Ord_id"].astype(int)
result["Prod_id"] = result["Prod_id"].astype(int)
result["Ship_id"] = result["Ship_id"].astype(int)
result["Cust_id"] = result["Cust_id"].astype(int)
result["Sales"] = result["Sales"].astype(int)
result["Discount"] = result["Discount"].astype(int)

# Reorder columns to match target schema
result = result[[
    "Order_Priority",
    "Ship_Mode",
    "Ord_id",
    "Prod_id",
    "Ship_id",
    "Cust_id",
    "Sales",
    "Discount"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)