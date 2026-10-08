import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

join_4_3 = pd.merge(source4, source3, how='inner', on='Prod_id')
join_4_3_2 = pd.merge(join_4_3, source2, how='inner', on='Ship_id')
join_4_3_2_0 = pd.merge(join_4_3_2, source0, how='inner', on='Ord_id')
join_all = pd.merge(join_4_3_2_0, source1, how='inner', on='Cust_id')

result = join_all[['Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)