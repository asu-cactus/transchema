import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

result_0 = pd.merge(source4, source2, on="Prod_id", how="inner")
result_1 = pd.merge(result_0, source0, on="Ord_id", how="inner")
result_2 = pd.merge(result_1, source3, on="Ship_id", how="inner")
result_3 = pd.merge(result_2, source1, on="Cust_id", how="inner")

final = result_3[["Prod_id", "Ord_id", "Ship_id", "Cust_id", "Sales", "Discount"]].copy()
final["Ord_id"] = final["Ord_id"].astype(str)
final["Ship_id"] = final["Ship_id"].astype(str)
final["Cust_id"] = final["Cust_id"].astype(str)
final["Sales"] = pd.to_numeric(final["Sales"], errors='coerce').fillna(0).astype(int)
final["Discount"] = pd.to_numeric(final["Discount"], errors='coerce').fillna(0).astype(int)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)