import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

pivot = s1.pivot_table(index=['Ord_id', 'Ship_id', 'Cust_id', 'Sales'], columns='Prod_id', values='Order_Quantity', aggfunc='sum').reset_index()
pivot_long = pivot.melt(id_vars=['Ord_id', 'Ship_id', 'Cust_id', 'Sales'], var_name='Prod_id', value_name='Order_Quantity').dropna(subset=['Order_Quantity'])

join1 = pivot_long.merge(s4[['Ship_id', 'Ship_Mode']], on='Ship_id', how='left')
join2 = join1.merge(s1[['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']], on=['Ord_id', 'Prod_id', 'Ship_id', 'Cust_id'], how='left')
join3 = join2.merge(s0[['Prod_id']], on='Prod_id', how='left')

result = join3[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

result['Order_Quantity'] = result['Order_Quantity'].astype(int)
result['Sales'] = result['Sales'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)