import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_4.csv", index_col=0)

# Join s0 and s4 on Order_ID
df = s0.merge(s4, on="Order_ID", how="inner")

# Join with s2 on Ord_id
df = df.merge(s2, on="Ord_id", how="inner")

# Join with s1 on Cust_id
df = df.merge(s1, on="Cust_id", how="inner")

# Join with s3 on Prod_id
df = df.merge(s3, on="Prod_id", how="inner")

# Group by Product_Category and sum Profit
result = df.groupby("Product_Category", as_index=False)["Profit"].sum()

# Keep only Profit column as per target schema
result = result[["Profit"]]

# Convert Profit to integer type as required
result["Profit"] = result["Profit"].round().astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)