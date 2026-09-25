import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

df_union = pd.concat([df1, df1], ignore_index=True)

df_grouped = df_union.groupby(['Broadband Initiative', 'state'], as_index=False).agg({
    'Federal': 'sum',
    'Percent': 'mean'
})

df_grouped['Broadband Initiative'] = df_grouped['Broadband Initiative'].astype('Int64')
df_grouped['Federal'] = df_grouped['Federal'].astype('Int64')
df_grouped['Percent'] = df_grouped['Percent'].astype(float)
df_grouped['state'] = df_grouped['state'].astype(str)

pop_df = df0.groupby('state', as_index=False)['population'].sum()
pop_df['population'] = pop_df['population'].astype('Int64')

result = pd.merge(df_grouped, pop_df, on='state', how='left')

result = result[['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)