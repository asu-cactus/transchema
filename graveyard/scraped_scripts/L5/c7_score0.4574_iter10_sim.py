import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_7/training_4.csv", index_col=0)

df = pd.merge(source4, source2, on="Ord_id")
df = pd.merge(df, source3, on="Ship_id")
df = pd.merge(df, source1, on="Cust_id")
df = pd.merge(df, source0, on="Prod_id")

df = df[["Product_Sub_Category", "Order_Quantity", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales", "Discount"]]

df["Order_Quantity"] = df["Order_Quantity"].astype(int)
df["Ord_id"] = df["Ord_id"].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
df["Prod_id"] = df["Prod_id"].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
df["Ship_id"] = df["Ship_id"].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
df["Cust_id"] = df["Cust_id"].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else x)
df["Sales"] = df["Sales"].round().astype(int)
df["Discount"] = df["Discount"].round().astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_7/target_multisource_mcts.csv", index=False)