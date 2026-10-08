import pandas as pd

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
union_result = pd.concat([s1, s2], ignore_index=True, sort=False)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
join_result_1 = pd.merge(union_result, s0[['Prod_id']], on='Prod_id', how='inner')

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, s3[['Cust_id']], on='Cust_id', how='inner')

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)
final_join = pd.merge(join_result_2, s4[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')

final = final_join.copy()
final['Ship_Date'] = final['Ship_Date'].astype(str)
final['Prod_id'] = final['Prod_id'].astype(str)
final['Ord_id'] = final['Ord_id'].str.replace('Ord_', '').astype(int)
final['Ship_id'] = final['Ship_id'].str.replace('SHP_', '').astype(int)
final['Cust_id'] = final['Cust_id'].str.replace('Cust_', '').astype(int)

final = final[['Ship_Date', 'Prod_id', 'Ord_id', 'Ship_id', 'Cust_id']]

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)