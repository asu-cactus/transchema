import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv", index_col=0)

grouped_0 = df0.groupby(['state', 'TechType'], as_index=False).agg(
    HighSpeed_count=('HighSpeed', 'count'),
    population_sum=('population', 'sum')
)

merged = pd.merge(grouped_0, df1, on='state', how='inner')

agg = merged.groupby('state', as_index=False).agg(
    Broadband_Initiative=('Broadband Initiative', 'sum'),
    Federal=('Federal', 'sum'),
    Percent=('Percent', 'mean'),
    HighSpeed_count_sum=('HighSpeed_count', 'sum'),
    population_sum_sum=('population_sum', 'sum')
)

agg.rename(columns={
    'HighSpeed_count_sum': 'Broadband Initiative',
    'population_sum_sum': 'population'
}, inplace=True)

agg = agg[['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']]

agg['Broadband Initiative'] = agg['Broadband Initiative'].astype(int)
agg['Federal'] = agg['Federal'].astype(int)
agg['Percent'] = agg['Percent'].astype(float)
agg['state'] = agg['state'].astype(str)
agg['population'] = agg['population'].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv", index=False)