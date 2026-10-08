import pandas as pd

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)
union_3_4 = pd.concat([s3, s4], sort=False, ignore_index=True)

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
join_1 = pd.merge(union_3_4, s1[['Ord_id', 'Order_Date']], on='Ord_id', how='inner')

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)
join_2 = pd.merge(join_1, s2[['Cust_id']], on='Cust_id', how='inner')

result = join_2[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']].copy()
result.rename(columns={'Order_Date': 'Ship_Date'}, inplace=True)
result['Ord_id'] = result['Ord_id'].str.replace('Ord_', '').astype(int)
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '').astype(int)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '').astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '').astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)