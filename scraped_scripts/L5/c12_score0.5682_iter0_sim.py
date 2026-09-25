import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

join1 = pd.merge(source4, source1, how='inner', left_on='Ord_id', right_on='Ord_id')
join2 = pd.merge(join1, source0, how='inner', left_on='Ship_id', right_on='Ship_id')
join3 = pd.merge(join2, source2, how='inner', left_on='Cust_id', right_on='Cust_id')
join4 = pd.merge(join3, source3, how='inner', left_on='Prod_id', right_on='Prod_id')

result = join4[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)