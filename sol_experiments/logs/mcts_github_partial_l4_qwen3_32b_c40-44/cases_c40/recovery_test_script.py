import pandas as pd

source0 = 'autopipeline-benchmarks/github-pipelines/length4_40/test_0.csv'
source1 = 'autopipeline-benchmarks/github-pipelines/length4_40/test_1.csv'
source2 = 'autopipeline-benchmarks/github-pipelines/length4_40/test_2.csv'
source3 = 'autopipeline-benchmarks/github-pipelines/length4_40/test_3.csv'

# Load and process all sources with index column correctly ignored
df0 = pd.read_csv(source0, index_col=0)
df0['y'] = df0['y'].astype(int)
df0['label'] = 1

df1 = pd.read_csv(source1, index_col=0)
df1['y'] = df1['y'].astype(int)
df1['label'] = 2

df2 = pd.read_csv(source2, index_col=0)
df2['y'] = df2['y'].astype(int)
df2['label'] = 3

df3 = pd.read_csv(source3, index_col=0)
df3['y'] = df3['y'].astype(int)
df3['label'] = 4

# Union all processed sources
combined = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Save to final target file with exactly target schema
combined.to_csv('autopipeline-benchmarks/github-pipelines/length4_40/target_multisource_mcts_recovery_test_val.csv', index=False)