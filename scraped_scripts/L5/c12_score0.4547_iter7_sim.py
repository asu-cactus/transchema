import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

s1_4 = pd.concat([s1, s4], ignore_index=True, sort=False)

join_0_4 = pd.merge(s4, s0[['Ship_Mode', 'Ship_id']], on='Ship_id', how='left')
join_1 = pd.merge(join_0_4, s1[['Ord_id', 'Order_Priority']], on='Ord_id', how='left')
join_2 = pd.merge(join_1, s2[['Cust_id']], on='Cust_id', how='left')
join_3 = pd.merge(join_2, s3[['Prod_id']], on='Prod_id', how='left')

result = join_3[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Order_Priority'] = result['Order_Priority'].astype('string')
result['Ship_Mode'] = result['Ship_Mode'].astype('string')
result['Ord_id'] = result['Ord_id'].apply(lambda x: int(x.split('_')[1]) if pd.notna(x) else None)
result['Prod_id'] = result['Prod_id'].apply(lambda x: int(x.split('_')[1]) if pd.notna(x) else None)
result['Ship_id'] = result['Ship_id'].apply(lambda x: int(x.split('_')[1]) if pd.notna(x) else None)
result['Cust_id'] = result['Cust_id'].apply(lambda x: int(x.split('_')[1]) if pd.notna(x) else None)
result['Sales'] = pd.to_numeric(result['Sales'], errors='coerce').fillna(0).astype(int)
result['Discount'] = pd.to_numeric(result['Discount'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)