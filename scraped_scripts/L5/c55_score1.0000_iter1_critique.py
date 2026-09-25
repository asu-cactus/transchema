import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

# Aggregate as per plan
agg_df = pd.DataFrame({
    'missing_count': [df['missing_count'].min()],
    'state': [df['state'].count()],
    'latitude': [df['latitude'].count()],
    'longitude': [df['longitude'].count()]
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length5_55/target_multisource_mcts.csv", index=False)