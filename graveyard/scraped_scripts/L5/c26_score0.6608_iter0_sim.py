import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_26/training_4.csv", index_col=0)

df_join_0 = pd.merge(df1, df2, on="Ord_id", how="inner")
df_join_1 = pd.merge(df_join_0, df4, on="Prod_id", how="inner")
df_join_2 = pd.merge(df_join_1, df0, on="Ship_id", how="inner")

result = df_join_2[["Product_Sub_Category", "Order_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "").astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "").astype(int)
result["Ship_id"] = result["Ship_id"].str.replace("SHP_", "").astype(int)
result["Cust_id"] = result["Cust_id"].str.replace("Cust_", "").astype(int)
result["Sales"] = result["Sales"].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_26/target_multisource_mcts.csv", index=False)