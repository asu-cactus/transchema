import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_21/training_4.csv", index_col=0)

df = pd.merge(source2, source4, on="Ord_id")
df = pd.merge(df, source0, on="Cust_id")
df = pd.merge(df, source1, on="Prod_id")
df = pd.merge(df, source3, on="Ship_id")

df = df[["Ship_id", "Order_Priority", "Ord_id", "Prod_id", "Cust_id", "Sales", "Discount"]]

df["Ord_id"] = df["Ord_id"].str.extract(r'(\d+)').astype(int)
df["Prod_id"] = df["Prod_id"].str.extract(r'(\d+)').astype(int)
df["Cust_id"] = df["Cust_id"].str.extract(r'(\d+)').astype(int)
df["Sales"] = df["Sales"].round().astype(int)
df["Discount"] = (df["Discount"] * 100).round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_21/target_multisource_mcts.csv", index=False)