import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

df = pd.merge(s2, s1, on="Ship_id", how="inner")
df = pd.merge(df, s4, on="Ord_id", how="inner")
df = pd.merge(df, s3, on="Cust_id", how="inner")

df["Ship_id"] = df["Ship_id"].str.replace("SHP_", "").astype(int)
df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "").astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "").astype(int)

result = df[["Ship_Date", "Prod_id", "Ord_id", "Ship_id", "Cust_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)