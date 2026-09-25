import pandas as pd
import glob

# Read all source files matching the pattern (assuming multiple source files exist)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_65/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables
df_list = [pd.read_csv(f, index_col=0) for f in files]
df = pd.concat(df_list, ignore_index=True)

# Group by 'year' and count the number of rows per year
result = df.groupby('year').size().reset_index(name='0')

# Ensure correct types
result['year'] = result['year'].astype(int)
result['0'] = result['0'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts.csv", index=False)