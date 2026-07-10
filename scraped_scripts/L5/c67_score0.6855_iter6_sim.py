import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

s1['Ship_id'] = s1['Ship_id'].str.replace('SHP_', '').astype(int)
s2['Ship_id'] = s2['Ship_id'].str.replace('SHP_', '').astype(int)
s2['Ord_id'] = s2['Ord_id'].str.replace('Ord_', '').astype(int)
s2['Cust_id'] = s2['Cust_id'].str.replace('Cust_', '').astype(int)
s4['Ord_id'] = s4['Ord_id'].str.replace('Ord_', '').astype(int)
s3['Cust_id'] = s3['Cust_id'].str.replace('Cust_', '').astype(int)

merged = pd.merge(s2, s1[['Ship_Date', 'Ship_id']], on='Ship_id', how='inner')
merged = pd.merge(merged, s0[['Prod_id']], on='Prod_id', how='inner')
merged = pd.merge(merged, s4[['Ord_id']], on='Ord_id', how='inner')
merged = pd.merge(merged, s3[['Cust_id']], on='Cust_id', how='inner')

merged['Ship_Date'] = merged['Ship_Date'].astype(str)
merged['Prod_id'] = merged['Prod_id'].astype(str)

result = merged[['Ship_Date', 'Prod_id', 'Ord_id', 'Ship_id', 'Cust_id']].copy()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)