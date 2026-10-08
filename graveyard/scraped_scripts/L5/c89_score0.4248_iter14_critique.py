import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

df = source4.merge(source0, on="Prod_id", how="inner")
df = df.merge(source1, on="Cust_id", how="inner")
df = df.merge(source2, on="Ord_id", how="inner")
df = df.merge(source3, on="Ship_id", how="inner")

agg_df = df.groupby(["Product_Category", "Customer_Segment", "Ship_Mode"], as_index=False).agg({"Profit": "sum"})

result = agg_df[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv", index=False)