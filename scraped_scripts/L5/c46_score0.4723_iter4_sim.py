import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

j1 = pd.merge(s4, s2, on="Ord_id", how="inner")
j2 = pd.merge(j1, s0, on="Cust_id", how="inner")
j3 = pd.merge(j2, s3, on="Prod_id", how="inner")

result = j3.groupby(["Customer_Name", "Ord_id", "Prod_id", "Ship_id"], as_index=False).size()

result = result.drop(columns=["size"], errors='ignore') if "size" in result.columns else result

result = j3[["Customer_Name", "Ord_id", "Prod_id", "Ship_id"]].drop_duplicates().reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)