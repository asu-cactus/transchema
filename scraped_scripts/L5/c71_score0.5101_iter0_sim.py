import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_71/training_4.csv", index_col=0)

join_0_4 = pd.merge(source0, source4[['Ord_id', 'Order_Priority']], on='Ord_id', how='inner')
join_0_4_2 = pd.merge(join_0_4, source2[['Ship_id', 'Ship_Mode']], on='Ship_id', how='inner')

result = join_0_4_2[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Sales'] = result['Sales'].round().astype('Int64')
result['Discount'] = (result['Discount'] * 100).round().astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_71/target_multisource_mcts.csv", index=False)