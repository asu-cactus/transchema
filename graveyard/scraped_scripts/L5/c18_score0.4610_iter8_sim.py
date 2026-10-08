import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

s1_pivot = s1.pivot_table(index=['Ord_id', 'Ship_id', 'Cust_id', 'Sales'], columns='Prod_id', values='Order_Quantity', aggfunc='sum').reset_index()

joined = pd.merge(s1_pivot, s4[['Ship_id', 'Ship_Mode']], on='Ship_id', how='left')

prod_cols = [col for col in joined.columns if col.startswith('Prod_')]

melted = joined.melt(id_vars=['Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Ship_Mode'], value_vars=prod_cols, var_name='Prod_id', value_name='Order_Quantity')

melted = melted[melted['Order_Quantity'] > 0]

def extract_int_id(s):
    return s.str.extract('(\d+)').astype(int)

melted['Ord_id'] = extract_int_id(melted['Ord_id'])
melted['Prod_id'] = extract_int_id(melted['Prod_id'])
melted['Ship_id'] = extract_int_id(melted['Ship_id'])
melted['Cust_id'] = extract_int_id(melted['Cust_id'])
melted['Order_Quantity'] = melted['Order_Quantity'].astype(int)
melted['Sales'] = melted['Sales'].astype(int)
melted['Ship_Mode'] = melted['Ship_Mode'].astype('string')

melted = melted[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

melted.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)