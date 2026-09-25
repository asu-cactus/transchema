import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

agg = s1.groupby("Order_Quantity").agg(
    Ord_id_count=("Ord_id", "count"),
    Sales_sum=("Sales", "sum"),
    Profit_sum=("Profit", "sum")
).reset_index()

joined_1 = pd.merge(agg, s1, on="Order_Quantity", how="inner")

joined_2 = pd.merge(joined_1, s4[["Ship_Mode", "Ship_id"]], on="Ship_id", how="inner")

result = joined_2[[
    "Order_Quantity",
    "Ship_Mode",
    "Ord_id",
    "Prod_id",
    "Ship_id",
    "Cust_id",
    "Sales"
]].copy()

result["Order_Quantity"] = result["Order_Quantity"].astype(int)
result["Ord_id"] = result["Ord_id"].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and x.startswith("Ord_") else pd.NA)
result["Prod_id"] = result["Prod_id"].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and x.startswith("Prod_") else pd.NA)
result["Ship_id"] = result["Ship_id"].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and x.startswith("SHP_") else pd.NA)
result["Cust_id"] = result["Cust_id"].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and x.startswith("Cust_") else pd.NA)
result["Sales"] = result["Sales"].round(0).astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)