import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

join_0 = pd.merge(df0, df1, on="Cust_id", how="inner")
join_1 = pd.merge(join_0, df2, on="Ord_id", how="inner")
join_2 = pd.merge(join_1, df3, on="Prod_id", how="inner")
join_3 = pd.merge(join_2, df4, on="Ship_id", how="inner")

result = join_3[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]].copy()

result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "").astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "").astype(int)
result["Cust_id"] = result["Cust_id"].str.replace("Cust_", "").astype(int)
result["Ship_id"] = result["Ship_id"].astype(str)
result["Customer_Name"] = result["Customer_Name"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)