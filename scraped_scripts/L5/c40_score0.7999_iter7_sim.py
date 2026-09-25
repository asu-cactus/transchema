import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_40/training_4.csv", index_col=0)

df = pd.merge(source1, source0, on="Cust_id", how="inner")
df = pd.merge(df, source3, on="Prod_id", how="inner")
df = pd.merge(df, source2, on="Ord_id", how="inner")
df = pd.merge(df, source4, on="Ship_id", how="inner")

result = df[["Ship_id", "Customer_Name", "Ord_id", "Prod_id", "Cust_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_40/target_multisource_mcts.csv", index=False)