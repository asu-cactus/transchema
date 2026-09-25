import pandas as pd

src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)

union_34 = pd.concat([src3, src4], ignore_index=True, sort=False)

join_1 = pd.merge(union_34, src1, how='inner', on='Ord_id')

join_2 = pd.merge(join_1, src2, how='inner', on='Cust_id')

result = join_2[['Ship_Date', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)