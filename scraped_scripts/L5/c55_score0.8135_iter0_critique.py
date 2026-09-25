import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_55/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_55/training_4.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

# Aggregate over all rows (no group by)
missing_count_sum = df_all['missing_count'].sum()
state_count_distinct = df_all['state'].nunique()
latitude_count_distinct = df_all['latitude'].nunique()
longitude_count_distinct = df_all['longitude'].nunique()

df_result = pd.DataFrame({
    'missing_count': [missing_count_sum],
    'state': [state_count_distinct],
    'latitude': [latitude_count_distinct],
    'longitude': [longitude_count_distinct]
})

df_result = df_result.astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length5_55/target_multisource_mcts.csv", index=False)