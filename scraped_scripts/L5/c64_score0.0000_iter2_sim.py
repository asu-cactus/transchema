import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_64/training_4.csv", index_col=0)

s1_renamed = s1.rename(columns={"Ship_id": "Ship_id"})
s3_renamed = s3.rename(columns={"Ord_id": "Ord_id", "Order_Date": "Ship_Date"})

union_result = pd.concat([s1_renamed, s3_renamed], ignore_index=True, sort=False)

join_result = pd.merge(union_result, s2, how="inner", on=["Ship_id", "Ord_id"])

join_result2 = pd.merge(join_result, s0[["Customer_Name", "Cust_id"]], how="left", on="Cust_id")

final_join = pd.merge(join_result2, s4[["Prod_id"]], how="left", on="Prod_id")

final = final_join[["Ship_Date", "Customer_Name", "Ord_id", "Prod_id", "Ship_id"]]

final["Ord_id"] = final["Ord_id"].str.replace("Ord_", "").astype(int)
final["Prod_id"] = final["Prod_id"].str.replace("Prod_", "").astype(int)
final["Ship_id"] = final["Ship_id"].str.replace("SHP_", "").astype(int)
final["Ship_Date"] = final["Ship_Date"].astype(str)
final["Customer_Name"] = final["Customer_Name"].astype(str)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_64/target_multisource_mcts.csv", index=False)