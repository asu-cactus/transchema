import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_50/training_4.csv", index_col=0)

j1 = pd.merge(s4, s3, on="Cust_id", how="inner")
j2 = pd.merge(j1, s0, on="Ship_id", how="inner")
j3 = pd.merge(j2, s1, on="Ord_id", how="inner")
j4 = pd.merge(j3, s2, on="Prod_id", how="inner")

result = j4[["Ship_Date", "Ord_id", "Prod_id", "Ship_id"]].drop_duplicates()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_50/target_multisource_mcts.csv", index=False)