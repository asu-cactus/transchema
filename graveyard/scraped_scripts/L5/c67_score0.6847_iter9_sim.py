import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_2.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_67/training_4.csv", index_col=0)

join_0 = pd.merge(source2, source0[['Prod_id']], on='Prod_id', how='inner')
join_1 = pd.merge(join_0, source1[['Ship_Date', 'Ship_id']], on='Ship_id', how='inner')
join_2 = pd.merge(join_1, source4[['Ord_id']], on='Ord_id', how='inner')

result = join_2[['Ship_Date', 'Prod_id', 'Ord_id', 'Ship_id', 'Cust_id']].copy()

result['Ord_id'] = result['Ord_id'].str.extract(r'(\d+)').astype(int)
result['Ship_id'] = result['Ship_id'].str.extract(r'(\d+)').astype(int)
result['Cust_id'] = result['Cust_id'].str.extract(r'(\d+)').astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_67/target_multisource_mcts.csv", index=False)