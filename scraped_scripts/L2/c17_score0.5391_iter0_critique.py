import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

# Aggregate source1 by 'state'
agg_source1 = source1.groupby('state', as_index=False).agg({
    'Broadband Initiative': 'sum',
    'Federal': 'sum',
    'Percent': 'mean'
})

# Merge aggregated broadband data with population data from source0 on 'state'
merged = pd.merge(agg_source1, source0[['state', 'population']], on='state', how='inner')

# Cast columns to target types
merged['Broadband Initiative'] = merged['Broadband Initiative'].astype(int)
merged['Federal'] = merged['Federal'].astype(int)
merged['Percent'] = merged['Percent'].astype(float)
merged['state'] = merged['state'].astype(str)
merged['population'] = merged['population'].astype(int)

# Reorder columns to match target schema
merged = merged[['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']]

merged.to_csv(output_path, index=False)