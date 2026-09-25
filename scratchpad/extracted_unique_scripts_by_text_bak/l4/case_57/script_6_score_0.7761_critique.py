import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_57/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_57/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_57/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_57/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df = df[df['TransTo'].notna()]

df_grouped = df.groupby('WarNum', as_index=False)['TransTo'].min()

# Reorder columns to match target schema ['TransTo', 'WarNum']
df_grouped = df_grouped[['TransTo', 'WarNum']]

df_grouped['TransTo'] = df_grouped['TransTo'].astype('Int64')
df_grouped['WarNum'] = df_grouped['WarNum'].astype('Int64')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_57/target_multisource_mcts.csv", index=False)