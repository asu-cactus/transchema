import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_4.csv", index_col=0)

# Join all sources stepwise on keys to get Profit column
# s0 and s4 share Order_ID / Ord_id (s0.Order_ID == s4.Order_ID)
# s4 and s2 share Ord_id
# s2 and s1 share Cust_id
# s2 and s3 share Prod_id

df = s0.merge(s4, on="Order_ID", how="inner")
df = df.merge(s2, left_on="Ord_id", right_on="Ord_id", how="inner")
df = df.merge(s1, on="Cust_id", how="inner")
df = df.merge(s3, on="Prod_id", how="inner")

# Extract Profit column and convert to integer as target schema requires integer Profit
result = df[["Profit"]].copy()
result["Profit"] = result["Profit"].round().astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)