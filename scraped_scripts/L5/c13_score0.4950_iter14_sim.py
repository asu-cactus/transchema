import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_13/training_4.csv", index_col=0)

join_0 = pd.merge(df1, df3, on="Prod_id", how="inner")
join_1 = pd.merge(join_0, df4, on="Ship_id", how="inner")
join_2 = pd.merge(join_1, df2, on="Cust_id", how="inner")

result = join_2[['Product_Sub_Category', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales', 'Discount']]

result['Sales'] = pd.to_numeric(result['Sales'], errors='coerce').fillna(0).astype(int)
result['Discount'] = pd.to_numeric(result['Discount'], errors='coerce').fillna(0).astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_13/target_multisource_mcts.csv", index=False)