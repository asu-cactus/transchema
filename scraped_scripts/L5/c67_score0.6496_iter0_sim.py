import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

j0 = pd.merge(s1, s2, on="Ship_id", how="inner")
j1 = pd.merge(j0, s3, on="Cust_id", how="inner")
j2 = pd.merge(j1, s4, on="Ord_id", how="inner")

j2["Ship_id"] = j2["Ship_id"].str.replace("SHP_", "").astype(int)
j2["Ord_id"] = j2["Ord_id"].str.replace("Ord_", "").astype(int)
j2["Cust_id"] = j2["Cust_id"].str.replace("Cust_", "").astype(int)

result = j2[["Ship_Date", "Prod_id", "Ord_id", "Ship_id", "Cust_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)