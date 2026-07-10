import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

df = s4.merge(s2, on="Cust_id", how="inner")
df = df.merge(s0, on="Ord_id", how="inner")
df = df.merge(s3, on="Prod_id", how="inner")
df = df.merge(s1, on="Ship_id", how="inner")

df = df[["Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "").astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "").astype(int)
df["Ship_id"] = df["Ship_id"].str.replace("SHP_", "").astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "").astype(int)
df["Sales"] = df["Sales"].round().astype(int)
df["Discount"] = (df["Discount"] * 100).round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)