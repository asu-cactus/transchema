import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_1.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_35/training_4.csv", index_col=0)

join_0_4 = pd.merge(source0, source4, on="Ord_id", how="inner")
join_0_4_1 = pd.merge(join_0_4, source1, on="Prod_id", how="inner")
join_all = pd.merge(join_0_4_1, source3, on="Cust_id", how="inner")

result = join_all[["Product_Category", "Ship_id", "Ord_id", "Prod_id", "Cust_id", "Sales"]].copy()

result["Ord_id"] = result["Ord_id"].str.extract(r'(\d+)').astype(int)
result["Prod_id"] = result["Prod_id"].str.extract(r'(\d+)').astype(int)
result["Cust_id"] = result["Cust_id"].str.extract(r'(\d+)').astype(int)
result["Ship_id"] = result["Ship_id"].astype(str)
result["Product_Category"] = result["Product_Category"].astype(str)
result["Sales"] = result["Sales"].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_35/target_multisource_mcts.csv", index=False)