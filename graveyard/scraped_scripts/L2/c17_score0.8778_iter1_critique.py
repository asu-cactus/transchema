import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

# Rename columns in df1 to match target schema exactly
df1 = df1.rename(columns={
    'Broadband Initiative': 'Broadband Initiative',
    'Federal': 'Federal',
    'Percent': 'Percent',
    'state': 'state'
})

# Join on 'state'
df_merged = pd.merge(df1, df0[['population', 'state']], on='state', how='inner')

# Group by the leftmost non-float unique columns in target schema
group_cols = ['Broadband Initiative', 'Federal', 'Percent', 'state']

# Aggregate population by sum
result = df_merged.groupby(group_cols, as_index=False).agg({'population': 'sum'})

# Ensure correct dtypes
result['Broadband Initiative'] = result['Broadband Initiative'].astype(int)
result['Federal'] = result['Federal'].astype(int)
result['Percent'] = result['Percent'].astype(float)
result['state'] = result['state'].astype(str)
result['population'] = result['population'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)