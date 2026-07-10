import pandas as pd

# Read source files
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_63/training_4.csv", index_col=0)

# Join df4 with all dimension tables on their keys
merged = pd.merge(df4, df0[['Ord_id']], on='Ord_id', how='inner')
merged = pd.merge(merged, df1[['Cust_id']], on='Cust_id', how='inner')
merged = pd.merge(merged, df2[['Prod_id']], on='Prod_id', how='inner')
merged = pd.merge(merged, df3[['Ship_id']], on='Ship_id', how='inner')

# Group by Prod_id and aggregate
agg_df = merged.groupby('Prod_id').agg(
    Ord_id=('Ord_id', pd.Series.nunique),
    Ship_id=('Ship_id', pd.Series.nunique),
    Cust_id=('Cust_id', pd.Series.nunique),
    Sales=('Sales', 'sum'),
    Discount=('Discount', 'sum')
).reset_index()

# Convert all columns except Prod_id to int
agg_df = agg_df.astype({
    'Ord_id': 'int64',
    'Ship_id': 'int64',
    'Cust_id': 'int64',
    'Sales': 'int64',
    'Discount': 'int64'
})

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_63/target_multisource_mcts.csv", index=False)