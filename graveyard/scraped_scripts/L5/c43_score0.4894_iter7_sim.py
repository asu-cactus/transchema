import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

result_0 = pd.merge(source4, source2, on="Ship_id", how="inner")
result_1 = pd.merge(result_0, source0, on="Ord_id", how="inner")
result_2 = pd.merge(result_1, source3, on="Prod_id", how="inner")
result_3 = pd.merge(result_2, source1, on="Cust_id", how="inner")

final = result_3[["Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]].copy()

final["Ord_id"] = final["Ord_id"].str.extract(r'(\d+)').astype(int)
final["Prod_id"] = final["Prod_id"].str.extract(r'(\d+)').astype(int)
final["Ship_id"] = final["Ship_id"].str.extract(r'(\d+)').astype(int)
final["Cust_id"] = final["Cust_id"].str.extract(r'(\d+)').astype(int)
final["Sales"] = final["Sales"].round().astype(int)
final["Ship_Mode"] = final["Ship_Mode"].astype(str)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)