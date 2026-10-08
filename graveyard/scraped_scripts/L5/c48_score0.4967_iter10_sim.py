import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_48/training_4.csv", index_col=0)

join1 = pd.merge(source4, source2, how='inner', left_on='Cust_id', right_on='Cust_id')
join2 = pd.merge(join1, source3, how='inner', left_on='Prod_id', right_on='Prod_id')
join3 = pd.merge(join2, source1, how='inner', left_on='Ship_id', right_on='Ship_id')
join4 = pd.merge(join3, source0, how='inner', left_on='Ord_id', right_on='Ord_id')

result = join4[['Order_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']].copy()

result['Ord_id'] = result['Ord_id'].str.replace('Ord_', '').astype(int)
result['Prod_id'] = result['Prod_id'].str.replace('Prod_', '').astype(int)
result['Ship_id'] = result['Ship_id'].str.replace('SHP_', '').astype(int)
result['Cust_id'] = result['Cust_id'].str.replace('Cust_', '').astype(int)
result['Sales'] = result['Sales'].round().astype(int)
result['Discount'] = (result['Discount'] * 100).round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_48/target_multisource_mcts.csv", index=False)