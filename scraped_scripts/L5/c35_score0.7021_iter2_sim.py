import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_4.csv", index_col=0)

joined_0 = pd.merge(source0, source3, on="Cust_id", how="inner")
joined_1 = pd.merge(joined_0, source1, on="Prod_id", how="inner")
joined_2 = pd.merge(joined_1, source4, on="Ord_id", how="inner")

df = joined_2[["Product_Category", "Ship_id", "Ord_id", "Prod_id", "Cust_id", "Sales"]].copy()

df["Ord_id"] = df["Ord_id"].str.replace("Ord_", "").astype(int)
df["Prod_id"] = df["Prod_id"].str.replace("Prod_", "").astype(int)
df["Cust_id"] = df["Cust_id"].str.replace("Cust_", "").astype(int)
df["Ship_id"] = df["Ship_id"].astype(str)
df["Product_Category"] = df["Product_Category"].astype(str)
df["Sales"] = df["Sales"].round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)