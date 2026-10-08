import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_43/training_4.csv", index_col=0)

union_result = pd.concat([s2, s4], ignore_index=True, sort=False)

join_result_1 = pd.merge(union_result, s0, on="Ord_id", how="inner")
join_result_2 = pd.merge(join_result_1, s1, on="Cust_id", how="inner")
join_result_3 = pd.merge(join_result_2, s3, on="Prod_id", how="inner")

target = join_result_3[['Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

target['Ord_id'] = target['Ord_id'].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else x)
target['Prod_id'] = target['Prod_id'].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else x)
target['Ship_id'] = target['Ship_id'].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else x)
target['Cust_id'] = target['Cust_id'].apply(lambda x: int(''.join(filter(str.isdigit, str(x)))) if pd.notnull(x) else x)
target['Sales'] = target['Sales'].astype(float).round().astype('Int64')

target.to_csv("autopipeline-benchmarks/github-pipelines/length5_43/target_multisource_mcts.csv", index=False)