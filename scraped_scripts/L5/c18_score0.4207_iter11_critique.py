import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_18/training_4.csv", index_col=0)

r0 = pd.merge(s1, s4, on="Ship_id", how="inner")
r1 = pd.merge(r0, s3, on="Cust_id", how="inner")
r2 = pd.merge(r1, s0, on="Prod_id", how="inner")
r3 = pd.merge(r2, s2, on="Ord_id", how="inner")

# Group by the leftmost non-float unique columns in target schema
group_cols = ['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id']

result = r3.groupby(group_cols, as_index=False).agg({'Sales': 'sum'})

# Ensure column order matches target schema exactly
result = result[['Order_Quantity', 'Ship_Mode', 'Ord_id', 'Prod_id', 'Ship_id', 'Cust_id', 'Sales']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_18/target_multisource_mcts.csv", index=False)