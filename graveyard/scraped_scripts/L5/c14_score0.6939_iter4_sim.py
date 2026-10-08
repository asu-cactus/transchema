import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_14/training_4.csv", index_col=0)

join_21 = pd.merge(source2, source1, on="Ship_id", how="inner")
join_210 = pd.merge(join_21, source0, on="Cust_id", how="inner")
join_2104 = pd.merge(join_210, source4, on="Ord_id", how="inner")
join_all = pd.merge(join_2104, source3, on="Prod_id", how="inner")

result = join_all[["Ship_id", "Ord_id", "Prod_id", "Cust_id"]].copy()

result["Ord_id"] = result["Ord_id"].str.replace("Ord_", "").astype(int)
result["Prod_id"] = result["Prod_id"].str.replace("Prod_", "").astype(int)
result["Cust_id"] = result["Cust_id"].str.replace("Cust_", "").astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_14/target_multisource_mcts.csv", index=False)