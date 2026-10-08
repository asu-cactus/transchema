import pandas as pd

source3_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
source3_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
union_result = pd.concat([source3_0, source3_1], ignore_index=True)

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
join_result_1 = pd.merge(union_result, source1, on="Prod_id", how="inner")

source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)
join_result_2 = pd.merge(join_result_1, source4, on="Ship_id", how="inner")

source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
join_result_3 = pd.merge(join_result_2, source2, on="Cust_id", how="inner")

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
final_join = pd.merge(join_result_3, source0, on="Ord_id", how="inner")

result = final_join[['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Ord_id'] = result['Ord_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else pd.NA)
result['Prod_id'] = result['Prod_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else pd.NA)
result['Ship_id'] = result['Ship_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else pd.NA)
result['Cust_id'] = result['Cust_id'].apply(lambda x: int(x.split('_')[1]) if isinstance(x, str) and '_' in x else pd.NA)

result['Sales'] = result['Sales'].astype(float).round().astype('Int64')
result['Discount'] = (result['Discount'].astype(float) * 100).round().astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)