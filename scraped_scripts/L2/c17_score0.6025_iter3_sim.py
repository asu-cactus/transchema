import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

agg_df0 = df0.groupby(['state', 'TechType'], as_index=False)['population'].sum()

merged = pd.merge(agg_df0, df1, on='state', how='inner')

merged = merged.rename(columns={'state': 'state', 'population': 'population',
                                'Broadband Initiative': 'Broadband Initiative',
                                'Federal': 'Federal', 'Percent': 'Percent'})

merged = merged[['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']]

merged['Broadband Initiative'] = merged['Broadband Initiative'].astype(int)
merged['Federal'] = merged['Federal'].astype(int)
merged['Percent'] = merged['Percent'].astype(float)
merged['state'] = merged['state'].astype(str)
merged['population'] = merged['population'].astype(int)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)