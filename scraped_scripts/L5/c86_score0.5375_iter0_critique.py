import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_4.csv", index_col=0)

# Join df2 with df0 on Ship_id
df = pd.merge(df2, df0[['Ship_id']], on='Ship_id', how='inner')

# Join with df1 on Cust_id
df = pd.merge(df, df1[['Cust_id', 'Region']], on='Cust_id', how='inner')

# Join with df3 on Prod_id
df = pd.merge(df, df3[['Prod_id']], on='Prod_id', how='inner')

# Join with df4 on Ord_id
df = pd.merge(df, df4[['Ord_id']], on='Ord_id', how='inner')

# Group by Region and sum Profit
agg = df.groupby('Region', as_index=False)['Profit'].sum()

# The target schema is only ['Profit'], so output only the Profit column
result = agg[['Profit']]

# Convert Profit to integer type as in target schema
result['Profit'] = result['Profit'].astype(int)

# Sort by Profit ascending to match target examples order (optional)
result = result.sort_values('Profit').reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)