import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_17/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_17/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped = df1.groupby(['Broadband Initiative', 'state'], as_index=False).agg({
    'Federal': 'sum',
    'Percent': 'mean',
    'Broadband Initiative': 'sum'
})

# Rename the summed Broadband Initiative column to integer type (it should be the same as group key)
grouped['Broadband Initiative'] = grouped['Broadband Initiative'].astype(int)

merged = pd.merge(grouped, df0[['state', 'population']], on='state', how='left')

merged['Federal'] = merged['Federal'].astype(int)
merged['Percent'] = merged['Percent'].astype(float)
merged['population'] = merged['population'].astype('Int64')  # allow NA if any

merged = merged[['Broadband Initiative', 'Federal', 'Percent', 'state', 'population']]

merged.to_csv(output_path, index=False)