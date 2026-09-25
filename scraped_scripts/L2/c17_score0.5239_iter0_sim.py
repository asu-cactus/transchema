import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

grouped_source1 = source1.groupby(['Broadband Initiative', 'state'], as_index=False).agg({
    'Federal': 'sum',
    'Percent': 'mean'
})

merged = pd.merge(grouped_source1, source0[['state', 'population']], on='state', how='inner')

merged['Broadband Initiative'] = merged['Broadband Initiative'].astype(int)
merged['Federal'] = merged['Federal'].astype(int)
merged['Percent'] = merged['Percent'].astype(float)
merged['state'] = merged['state'].astype(str)
merged['population'] = merged['population'].astype(int)

merged = merged[['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']]

merged.to_csv(output_path, index=False)