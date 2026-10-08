import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

result_0 = pd.merge(df4, df2, on="Ship_id", how="inner")
result_1 = pd.merge(result_0, df0, on="Ord_id", how="inner")
result_2 = pd.merge(result_1, df1, on="Cust_id", how="inner")
result_3 = pd.merge(result_2, df3, on="Prod_id", how="inner")

grouped = result_3.groupby("Ship_Mode").agg({
    "Ord_id": "count",
    "Prod_id": "count",
    "Ship_id": "count",
    "Cust_id": "count",
    "Sales": "sum"
}).reset_index()

grouped["Ord_id"] = grouped["Ord_id"].astype(int)
grouped["Prod_id"] = grouped["Prod_id"].astype(int)
grouped["Ship_id"] = grouped["Ship_id"].astype(int)
grouped["Cust_id"] = grouped["Cust_id"].astype(int)
grouped["Sales"] = grouped["Sales"].round().astype(int)

grouped = grouped[["Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)