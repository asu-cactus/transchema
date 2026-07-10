import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_46/training_4.csv", index_col=0)

pivot = src0[['Customer_Name', 'Cust_id']].drop_duplicates().rename(columns={'Cust_id':'Cust_id'})
pivot_result = pivot

join1 = pd.merge(pivot_result, src4, left_on='Cust_id', right_on='Cust_id', how='inner')

join2 = pd.merge(join1, src2[['Ord_id']], on='Ord_id', how='inner')

join3 = pd.merge(join2, src3[['Prod_id']], on='Prod_id', how='inner')

result = join3[['Customer_Name', 'Ord_id', 'Prod_id', 'Ship_id']]

result['Ord_id'] = result['Ord_id'].str.extract('(\d+)').astype(int)
result['Prod_id'] = result['Prod_id'].str.extract('(\d+)').astype(int)
result['Ship_id'] = result['Ship_id'].str.extract('(\d+)').astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_46/target_multisource_mcts.csv", index=False)