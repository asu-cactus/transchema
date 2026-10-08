import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_4.csv", index_col=0)

j0 = pd.merge(s0, s1, on="Prod_id", how="inner")
j1 = pd.merge(j0, s2, on="Ship_id", how="inner")
j2 = pd.merge(j1, s3, on="Ord_id", how="inner")
j3 = pd.merge(j2, s4, on="Cust_id", how="inner")

agg_df = j3.groupby(["Region", "Customer_Segment"], as_index=False).agg({"Profit": "sum"})

result = agg_df[["Profit"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_75/target_multisource_mcts.csv", index=False)