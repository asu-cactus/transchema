import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_75/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_75/training_38.csv",
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

# Convert columns to correct types without assignment
df['anime_id'] = pd.to_numeric(df['anime_id'], errors='coerce').astype('Int64')
df['name'] = df['name'].astype(str)
df['genre'] = df['genre'].astype(str)
df['type'] = df['type'].astype(str)
df['episodes'] = pd.to_numeric(df['episodes'], errors='coerce').astype('Int64')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce').astype(float)
df['members'] = pd.to_numeric(df['members'], errors='coerce').astype('Int64')

# Define aggregation functions
def first_non_null(series):
    return series.dropna().iloc[0] if not series.dropna().empty else pd.NA

agg_dict = {
    'genre': first_non_null,
    'type': first_non_null,
    'episodes': first_non_null,
    'rating': 'mean',
    'members': 'max',
}

grouped = df.groupby(['anime_id', 'name'], as_index=False).agg(agg_dict)

# Ensure types after aggregation
grouped['anime_id'] = grouped['anime_id'].astype('Int64')
grouped['name'] = grouped['name'].astype(str)
grouped['genre'] = grouped['genre'].astype(str)
grouped['type'] = grouped['type'].astype(str)
grouped['episodes'] = grouped['episodes'].astype('Int64')
grouped['rating'] = grouped['rating'].astype(float)
grouped['members'] = grouped['members'].astype('Int64')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_75/target_multisource_mcts.csv", index=False)