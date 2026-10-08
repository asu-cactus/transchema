import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

join_1 = pd.merge(source4, source2, how='inner', left_on='Cust_id', right_on='Cust_id')
join_2 = pd.merge(join_1, source1, how='inner', left_on='Ord_id', right_on='Ord_id')
join_3 = pd.merge(join_2, source0, how='inner', left_on='Ship_id', right_on='Ship_id')

result = join_3[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']].copy()

result['Ord_id'] = result['Ord_id'].astype(str)
result['Prod_id'] = result['Prod_id'].astype(str)
result['Ship_id'] = result['Ship_id'].astype(str)
result['Cust_id'] = result['Cust_id'].astype(str)
result['Order_Priority'] = result['Order_Priority'].astype(str)
result['Ship_Mode'] = result['Ship_Mode'].astype(str)
result['Sales'] = pd.to_numeric(result['Sales'], errors='coerce').fillna(0).astype(int)
result['Discount'] = pd.to_numeric(result['Discount'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)