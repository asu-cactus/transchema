import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

joined_4_1 = pd.merge(source4, source1, on="Cust_id", how="inner")
joined_4_1_0 = pd.merge(joined_4_1, source0, on="Ord_id", how="inner")
final_join = pd.merge(joined_4_1_0, source3, on="Ship_id", how="inner")

result = final_join[["Prod_id", "Ord_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()

result["Ord_id"] = result["Ord_id"].str.extract(r'(\d+)').astype(int)
result["Ship_id"] = result["Ship_id"].str.extract(r'(\d+)').astype(int)
result["Cust_id"] = result["Cust_id"].str.extract(r'(\d+)').astype(int)
result["Sales"] = result["Sales"].round().astype(int)
result["Discount"] = (result["Discount"] * 100).round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)