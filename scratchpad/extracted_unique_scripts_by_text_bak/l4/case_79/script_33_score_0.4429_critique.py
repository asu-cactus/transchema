import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_79/training_4.csv", index_col=0)

# Concatenate all source tables (UNION)
df_all = pd.concat([s0, s1, s2, s3, s4], ignore_index=True)

# Ensure correct dtypes
df_all['hero'] = df_all['hero'].astype(str)
df_all['disadvantage'] = pd.to_numeric(df_all['disadvantage'], errors='coerce')
df_all['winrate'] = pd.to_numeric(df_all['winrate'], errors='coerce')
df_all['matches'] = pd.to_numeric(df_all['matches'], errors='coerce').astype('Int64')

# Group by 'hero' and aggregate:
# disadvantage: mean
# winrate: mean
# matches: sum
df_grouped = df_all.groupby('hero', as_index=False).agg({
    'disadvantage': 'mean',
    'winrate': 'mean',
    'matches': 'sum'
})

# Write output
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_79/target_multisource_mcts.csv", index=False)