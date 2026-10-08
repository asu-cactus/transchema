import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

pivoted = source0.pivot(index='Ship_id', columns='Ship_Mode', values='Ship_id')
unpivoted = pivoted.reset_index().melt(id_vars='Ship_id', value_name='Ship_id_val')
unpivoted = unpivoted.drop(columns=['Ship_id_val'])
unpivoted = unpivoted.rename(columns={'variable': 'Ship_Mode'})

joined_4 = pd.merge(unpivoted, source4, on='Ship_id', how='inner')
joined_1 = pd.merge(joined_4, source1, on='Ord_id', how='inner')
joined_2 = pd.merge(joined_1, source2, on='Cust_id', how='inner')
joined_3 = pd.merge(joined_2, source3, on='Prod_id', how='inner')

result = joined_3[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Ord_id'] = result['Ord_id'].str.extract('(\d+)').astype(int)
result['Prod_id'] = result['Prod_id'].str.extract('(\d+)').astype(int)
result['Ship_id'] = result['Ship_id'].str.extract('(\d+)').astype(int)
result['Cust_id'] = result['Cust_id'].str.extract('(\d+)').astype(int)
result['Sales'] = result['Sales'].astype(int)
result['Discount'] = (result['Discount'] * 100).round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)