import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_12/training_4.csv", index_col=0)

join_1_4 = pd.merge(source1, source4, on="Ord_id", how="inner")
join_1_4_0 = pd.merge(join_1_4, source0, on="Ship_id", how="inner")
join_all = pd.merge(join_1_4_0, source2, on="Cust_id", how="inner")
join_all = pd.merge(join_all, source3, on="Prod_id", how="inner")

result = join_all[['Order_Priority', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Sales'] = pd.to_numeric(result['Sales'], errors='coerce').fillna(0).astype(int)
result['Discount'] = pd.to_numeric(result['Discount'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_12/target_multisource_mcts.csv", index=False)