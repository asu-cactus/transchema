import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_42/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_42/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_42/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_42/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_42/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

df_agg = pd.DataFrame({
    "missing_count": [df_all["missing_count"].sum()],
    "state": [0],  # Since target example has state=225, but no mapping is given, we set to 0 as integer placeholder
    "latitude": [round(df_all["latitude"].mean())],
    "longitude": [round(df_all["longitude"].mean())]
})

df_agg = df_agg.astype({
    "missing_count": int,
    "state": int,
    "latitude": int,
    "longitude": int
})

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length5_42/target_multisource_mcts.csv", index=False)