import pandas as pd
import re

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

# Join source1 and source0 on Prod_id
df = pd.merge(source1, source0, on="Prod_id", how="inner")
# Join with source2 on Ord_id
df = pd.merge(df, source2, on="Ord_id", how="inner")
# Join with source3 on Cust_id
df = pd.merge(df, source3, on="Cust_id", how="inner")
# Join with source4 on Ship_id
df = pd.merge(df, source4, on="Ship_id", how="inner")

# Group by Ship_Mode, Ord_id, Prod_id, Ship_id, Cust_id and sum Order_Quantity and Sales
agg = df.groupby(["Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id"], as_index=False).agg({
    "Order_Quantity": "sum",
    "Sales": "sum"
})

# Convert IDs from strings like "Ord_1082" to integers 1082
def extract_int_id(s):
    # Extract trailing digits from string
    match = re.search(r'(\d+)$', s)
    return int(match.group(1)) if match else None

agg["Ord_id"] = agg["Ord_id"].map(extract_int_id)
agg["Prod_id"] = agg["Prod_id"].map(extract_int_id)
agg["Ship_id"] = agg["Ship_id"].map(extract_int_id)
agg["Cust_id"] = agg["Cust_id"].map(extract_int_id)

# Convert Order_Quantity and Sales to int (Sales rounded)
agg["Order_Quantity"] = agg["Order_Quantity"].astype(int)
agg["Sales"] = agg["Sales"].round().astype(int)

# Reorder columns to match target schema
agg = agg[["Order_Quantity", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)