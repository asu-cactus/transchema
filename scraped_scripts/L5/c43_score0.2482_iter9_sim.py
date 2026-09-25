import pandas as pd

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)
union_result = pd.concat([s2, s4], ignore_index=True, sort=False)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
join_result_1 = pd.merge(union_result, s0, on="Ord_id", how="inner")

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s1, on="Cust_id", how="inner")

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
final_join = pd.merge(join_result_2, s3, on="Prod_id", how="inner")

final = final_join[["Ship_Mode", "Ord_id", "Prod_id", "Ship_id", "Cust_id", "Sales"]]

final["Sales"] = final["Sales"].fillna(0).astype(int)
final["Ord_id"] = final["Ord_id"].astype(str)
final["Prod_id"] = final["Prod_id"].astype(str)
final["Ship_id"] = final["Ship_id"].astype(str)
final["Cust_id"] = final["Cust_id"].astype(str)
final["Ship_Mode"] = final["Ship_Mode"].astype(str)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)