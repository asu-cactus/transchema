import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_11/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_11/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_11/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_11/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_11/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

df_grouped = df_all.groupby(['missing_count', 'state'], as_index=False).agg({
    'latitude': 'mean',
    'longitude': 'mean'
})

df_grouped['missing_count'] = df_grouped['missing_count'].astype(int)
df_grouped['latitude'] = df_grouped['latitude'].round().astype(int)
df_grouped['longitude'] = df_grouped['longitude'].round().astype(int)

state_to_int = {state: i for i, state in enumerate(sorted(df_grouped['state'].unique()))}
df_grouped['state'] = df_grouped['state'].map(state_to_int).astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_11/target_multisource_mcts.csv", index=False)