import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

# UNION all source tables
union_df = pd.concat([s0, s1, s2, s3], ignore_index=True)

# Drop rows with NaN in TransTo or WarNum
union_df = union_df.dropna(subset=['TransTo', 'WarNum'])

# Convert to int
union_df['TransTo'] = union_df['TransTo'].astype(int)
union_df['WarNum'] = union_df['WarNum'].astype(int)

# Group by TransTo, aggregate WarNum by first
result = union_df.groupby('TransTo', as_index=False).agg({'WarNum':'first'})

# Reorder columns to match target schema ['TransTo', 'WarNum']
result = result[['TransTo', 'WarNum']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)