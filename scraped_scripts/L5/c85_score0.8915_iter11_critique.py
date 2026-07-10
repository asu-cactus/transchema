import pandas as pd

# Read source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_85/training_4.csv", index_col=0)

# Join Source4 with Source1 on Ord_id
j0 = pd.merge(s4, s1, how='inner', left_on='Ord_id', right_on='Ord_id')

# Join with Source0 on Ship_id
j1 = pd.merge(j0, s0, how='inner', left_on='Ship_id', right_on='Ship_id')

# Join with Source2 on Cust_id
j2 = pd.merge(j1, s2, how='inner', left_on='Cust_id', right_on='Cust_id')

# Join with Source3 on Prod_id
j3 = pd.merge(j2, s3, how='inner', left_on='Prod_id', right_on='Prod_id')

# Group by 'Region' and aggregate sum of 'Sales'
agg = j3.groupby('Region', as_index=False)['Sales'].sum()

# Output only the 'Sales' column as per target schema
result = agg[['Sales']].copy()

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_85/target_multisource_mcts.csv", index=False)