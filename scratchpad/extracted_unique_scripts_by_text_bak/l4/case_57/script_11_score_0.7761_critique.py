import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv", index_col=0)

df = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Drop rows with NaN in either TransTo or WarNum
df = df.dropna(subset=['TransTo', 'WarNum'])

# Convert to integer type as per target schema
df['TransTo'] = df['TransTo'].astype(int)
df['WarNum'] = df['WarNum'].astype(int)

# Remove duplicates to match unique tuples in target
df = df.drop_duplicates(subset=['TransTo', 'WarNum'])

# Group by both columns to ensure uniqueness (no aggregation needed)
df_grouped = df.groupby(['TransTo', 'WarNum'], dropna=False).size().reset_index().drop(columns=0)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)