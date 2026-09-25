import pandas as pd
import glob

# Read all source CSV files matching the pattern (assuming multiple source files)
file_pattern = "autopipeline-benchmarks/github-pipelines/length1_20/training_*.csv"
files = sorted(glob.glob(file_pattern))

# Read and concatenate all source tables (UNION)
dfs = [pd.read_csv(f, index_col=0) for f in files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by 'sex' and 'smoker' and aggregate mean on 'total_bill', 'tip', 'size'
result = df_all.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

# Write output with exact target schema column order
result = result[['sex', 'smoker', 'total_bill', 'tip', 'size']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)