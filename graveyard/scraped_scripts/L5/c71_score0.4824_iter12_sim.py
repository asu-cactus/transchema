import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

df = pd.merge(s0, s2, on="Ship_id", how="inner")
df = pd.merge(df, s1, on="Cust_id", how="inner")
df = pd.merge(df, s3, on="Prod_id", how="inner")
df = pd.merge(df, s4, on="Ord_id", how="inner")

agg = df.groupby([
    "Order_Priority",
    "Ship_Mode",
    "Ord_id",
    "Prod_id",
    "Ship_id",
    "Cust_id"
], dropna=False).agg({
    "Sales": "sum",
    "Discount": "sum"
}).reset_index()

agg["Sales"] = agg["Sales"].round().astype(int)
agg["Discount"] = agg["Discount"].round().astype(int)
agg["Ord_id"] = agg["Ord_id"].str.extract(r'(\d+)').astype(int)
agg["Prod_id"] = agg["Prod_id"].str.extract(r'(\d+)').astype(int)
agg["Ship_id"] = agg["Ship_id"].str.extract(r'(\d+)').astype(int)
agg["Cust_id"] = agg["Cust_id"].str.extract(r'(\d+)').astype(int)
agg["Order_Priority"] = agg["Order_Priority"].astype(str)
agg["Ship_Mode"] = agg["Ship_Mode"].astype(str)

agg = agg[["Order_Priority", "Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)