import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_65/training_4.csv", index_col=0)

df = pd.merge(s0, s4, on="Ord_id", how="inner")
df = pd.merge(df, s2, on="Cust_id", how="inner")
df = pd.merge(df, s3, on="Prod_id", how="inner")

df_out = df[["Prod_id", "Order_Priority", "Ord_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()

df_out["Ord_id"] = df_out["Ord_id"].str.replace("Ord_", "").astype(int)
df_out["Ship_id"] = df_out["Ship_id"].str.replace("SHP_", "").astype(int)
df_out["Cust_id"] = df_out["Cust_id"].str.replace("Cust_", "").astype(int)
df_out["Sales"] = df_out["Sales"].round().astype(int)
df_out["Discount"] = (df_out["Discount"] * 100).round().astype(int)

df_out.to_csv("autopipeline-benchmarks/github-pipelines/length5_65/target_multisource_mcts.csv", index=False)