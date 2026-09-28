import pandas as pd
import glob

# Read all source files matching the pattern
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_11/training_*.csv"
files = glob.glob(file_pattern)

# Read and concatenate all source tables (UNION)
df_list = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

# Group by 'sex' and sum 'births'
result = df_all.groupby('sex', as_index=False)['births'].sum()

# Ensure correct types
result['sex'] = result['sex'].astype(str)
result['births'] = result['births'].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)