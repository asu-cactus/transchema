import pandas as pd

# Read and union all 60 source files
dfs = []
for i in range(60):
    df = pd.read_csv(f"autopipeline-benchmarks/github-pipelines/length1_60/training_{i}.csv", index_col=0)
    dfs.append(df)
df_all = pd.concat(dfs, ignore_index=True)

# Filter rows where type == 'Urban'
df_filtered = df_all[df_all['type'] == 'Urban']

# Group by 'type' and sum 'driver_count'
result = df_filtered.groupby('type', as_index=False)['driver_count'].sum()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)