import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

grouped_source4 = source4.groupby('Prod_id', as_index=False).agg({
    'Ord_id': 'first',
    'Ship_id': 'first',
    'Cust_id': 'first',
    'Sales': 'first',
    'Discount': 'first'
})

joined_1 = pd.merge(grouped_source4, source2[['Prod_id']], on='Prod_id', how='left')
joined_2 = pd.merge(joined_1, source0[['Ord_id']], on='Ord_id', how='left')
joined_3 = pd.merge(joined_2, source1[['Cust_id']], on='Cust_id', how='left')
final_join = pd.merge(joined_3, source3[['Ship_id']], on='Ship_id', how='left')

result = final_join[['Prod_id', 'Ord_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Ord_id'] = result['Ord_id'].apply(lambda x: int(x.split('_')[1]) if pd.notnull(x) else x)
result['Ship_id'] = result['Ship_id'].apply(lambda x: int(x.split('_')[1]) if pd.notnull(x) else x)
result['Cust_id'] = result['Cust_id'].apply(lambda x: int(x.split('_')[1]) if pd.notnull(x) else x)
result['Sales'] = result['Sales'].astype(int)
result['Discount'] = (result['Discount'] * 100).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)