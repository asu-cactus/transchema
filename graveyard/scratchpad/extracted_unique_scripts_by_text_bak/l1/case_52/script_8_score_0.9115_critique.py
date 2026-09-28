import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files)
file_pattern = 'autopipeline-benchmarks/github-pipelines/length1_52/training_*.csv'
files = glob.glob(file_pattern)

# Read and concatenate all source tables
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'condition' and count 'click' occurrences
result = df_all.groupby('condition', as_index=False)['click'].count()

# Rename 'click' count column to '0' as per target schema
result = result.rename(columns={'click': '0'})

# Ensure correct types
result['condition'] = result['condition'].astype(int)
result['0'] = result['0'].astype(int)

# Write output
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv', index=False)