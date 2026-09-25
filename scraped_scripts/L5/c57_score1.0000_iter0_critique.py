import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_57/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_57/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_57/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_57/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_57/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = pd.DataFrame({
    'missing_count': [df_all['missing_count'].sum()],
    'state': [df_all['state'].count()],
    'latitude': [round(df_all['latitude'].mean())],
    'longitude': [round(df_all['longitude'].mean())]
})

agg = agg.astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_57/target_multisource_mcts.csv", index=False)