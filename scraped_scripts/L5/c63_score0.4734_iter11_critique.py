import pandas as pd
import re

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

# Join source4 and source2 on Prod_id
join_42 = pd.merge(source4, source2, on="Prod_id", how="inner")

# Join with source0 on Ord_id
join_420 = pd.merge(join_42, source0, on="Ord_id", how="inner")

# Join with source3 on Ship_id
join_4203 = pd.merge(join_420, source3, on="Ship_id", how="inner")

# Join with source1 on Cust_id
join_all = pd.merge(join_4203, source1, on="Cust_id", how="inner")

# Extract numeric part from Ord_id, Ship_id, Cust_id to convert to int
def extract_int(s):
    if pd.isna(s):
        return None
    m = re.search(r'(\d+)', str(s))
    return int(m.group(1)) if m else None

join_all["Ord_id"] = join_all["Ord_id"].apply(extract_int)
join_all["Ship_id"] = join_all["Ship_id"].apply(extract_int)
join_all["Cust_id"] = join_all["Cust_id"].apply(extract_int)

# Group by Prod_id, Ord_id, Ship_id, Cust_id and aggregate Sales and Discount by sum
grouped = join_all.groupby(["Prod_id", "Ord_id", "Ship_id", "Cust_id"], as_index=False).agg({
    "Sales": "sum",
    "Discount": "sum"
})

# Convert Sales and Discount to int (after sum)
grouped["Sales"] = grouped["Sales"].fillna(0).astype(int)
grouped["Discount"] = grouped["Discount"].fillna(0).astype(int)

# Select columns in target schema order
result = grouped[["Prod_id", "Ord_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)