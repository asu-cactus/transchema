import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

r0 = pd.merge(s4, s3, how='inner', left_on='Prod_id', right_on='Prod_id')

r1 = pd.merge(r0, s0, how='inner', left_on='Ord_id', right_on='Ord_id')

r2 = pd.merge(r1, s2, how='inner', left_on='Cust_id', right_on='Cust_id')

r3 = pd.merge(r2, s1, how='inner', left_on='Ship_id', right_on='Ship_id')

out = r3[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']].copy()

out['Ord_id'] = out['Ord_id'].str.replace('Ord_', '').astype(int)
out['Prod_id'] = out['Prod_id'].str.replace('Prod_', '').astype(int)
out['Ship_id'] = out['Ship_id'].str.replace('SHP_', '').astype(int)
out['Cust_id'] = out['Cust_id'].str.replace('Cust_', '').astype(int)
out['Sales'] = out['Sales'].round().astype(int)
out['Discount'] = (out['Discount'] * 100).round().astype(int)

out.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)