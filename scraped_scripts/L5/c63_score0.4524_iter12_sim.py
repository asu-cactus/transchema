import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

join_41 = pd.merge(s4, s1, on="Cust_id", how="inner")
join_413 = pd.merge(join_41, s3, on="Ship_id", how="inner")
join_4132 = pd.merge(join_413, s2, on="Prod_id", how="inner")
join_41320 = pd.merge(join_4132, s0, on="Ord_id", how="inner")

df = join_41320[["Prod_id", "Ord_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()

df["Prod_id"] = df["Prod_id"].astype(str)
df["Ord_id"] = df["Ord_id"].str.extract(r'(\d+)').astype(int)
df["Ship_id"] = df["Ship_id"].str.extract(r'(\d+)').astype(int)
df["Cust_id"] = df["Cust_id"].str.extract(r'(\d+)').astype(int)
df["Sales"] = df["Sales"].round().astype(int)
df["Discount"] = (df["Discount"] * 100).round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)