import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

r1 = pd.merge(s1, s4, on="Ord_id", how="inner")
r2 = pd.merge(r1, s0, on="Ship_id", how="inner")
r3 = pd.merge(r2, s2, on="Cust_id", how="inner")
r4 = pd.merge(r3, s3, on="Prod_id", how="inner")

grouped = r4.groupby(
    ["Order_Priority", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id"],
    as_index=False,
).agg({"Sales": "sum", "Discount": "sum"})

grouped["Ord_id"] = grouped["Ord_id"].str.extract(r'(\d+)').astype(int)
grouped["Prod_id"] = grouped["Prod_id"].str.extract(r'(\d+)').astype(int)
grouped["Ship_id"] = grouped["Ship_id"].str.extract(r'(\d+)').astype(int)
grouped["Cust_id"] = grouped["Cust_id"].str.extract(r'(\d+)').astype(int)

grouped["Sales"] = grouped["Sales"].round().astype(int)
grouped["Discount"] = grouped["Discount"].round().astype(int)

grouped = grouped.rename(columns={
    "Order_Priority": "Order_Priority",
    "Ship_Mode": "Ship_Mode",
    "Ord_id": "Ord_id",
    "Prod_id": "Prod_id",
    "Ship_id": "Ship_id",
    "Cust_id": "Cust_id",
    "Sales": "Sales",
    "Discount": "Discount"
})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)