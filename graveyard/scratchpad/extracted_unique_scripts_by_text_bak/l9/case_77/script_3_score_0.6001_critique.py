import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_77/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_77/training_38.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types without assignment
df['anime_id'] = df['anime_id'].astype(int)
df['name'] = df['name'].astype(str)
df['genre'] = df['genre'].astype(str)
df['type'] = df['type'].astype(str)
df['episodes'] = pd.to_numeric(df['episodes'], errors='coerce').fillna(0).astype(int)
df['rating'] = pd.to_numeric(df['rating'], errors='coerce').astype(float)
df['members'] = pd.to_numeric(df['members'], errors='coerce').fillna(0).astype(int)

# Group by anime_id and name, aggregate other columns
agg_df = df.groupby(['anime_id', 'name'], as_index=False).agg({
    'genre': 'first',
    'type': 'first',
    'episodes': 'max',
    'rating': 'mean',
    'members': 'max'
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_77/target_multisource_mcts.csv", index=False)