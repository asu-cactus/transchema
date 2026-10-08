import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df1.groupby(['Broadband Initiative', 'state'], as_index=False).agg(
    Federal=('Federal', 'count'),
    Percent=('Percent', 'max')
)

merged = pd.merge(grouped, df0[['population', 'state']], on='state', how='left')

merged = merged.rename(columns={'Broadband Initiative': 'Broadband Initiative', 'Federal': 'Federal', 'Percent': 'Percent', 'state': 'state', 'population': 'population'})

merged['Broadband Initiative'] = merged['Broadband Initiative'].astype(int)
merged['Federal'] = merged['Federal'].astype(int)
merged['Percent'] = merged['Percent'].astype(float)
merged['state'] = merged['state'].astype(str)
merged['population'] = merged['population'].fillna(0).astype(int)

merged.to_csv(target_path, index=False)