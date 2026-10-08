import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_4.csv", index_col=0)

# Join Source5_86_2 with Source5_86_0 on Ship_id
df = pd.merge(s2, s0, on='Ship_id', how='inner')

# Join with Source5_86_1 on Cust_id
df = pd.merge(df, s1, on='Cust_id', how='inner')

# Join with Source5_86_3 on Prod_id
df = pd.merge(df, s3, on='Prod_id', how='inner')

# Join with Source5_86_4 on Ord_id
df = pd.merge(df, s4, on='Ord_id', how='inner')

# Group by Ord_id and sum Profit
result = df.groupby('Ord_id', as_index=False)['Profit'].sum()

# Convert Profit to integer type (rounding if needed)
result['Profit'] = result['Profit'].round().astype('Int64')

# Output only the Profit column as per target schema
result[['Profit']].to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)