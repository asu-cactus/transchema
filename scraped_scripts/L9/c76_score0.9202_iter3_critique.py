import pandas as pd
from functools import reduce

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_76/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_14.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_15.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_16.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_17.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_18.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_19.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_20.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_21.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_22.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_23.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_24.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_25.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_26.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_27.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_28.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_29.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_30.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_31.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_32.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_33.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_34.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_35.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_36.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_37.csv",
    "autopipeline-benchmarks/github-pipelines/length9_76/training_38.csv",
]

# Read all dataframes with index_col=0
dfs = [pd.read_csv(path, index_col=0) for path in paths]

# Rename columns to avoid collision after join: add suffix _i for i-th dataframe
for i, df in enumerate(dfs):
    df.columns = [f"{col}_{i}" for col in df.columns]

# The key column is 'anime_id_i' for each df, all should be the same key
# We'll join all dfs on their anime_id columns

# Start with first df
df_joined = dfs[0]

for i in range(1, len(dfs)):
    df_joined = df_joined.merge(
        dfs[i],
        left_on=f"anime_id_0",
        right_on=f"anime_id_{i}",
        how="outer",
        suffixes=("", f"_{i}")
    )

# After join, we have multiple genre columns: genre_0, genre_1, ..., genre_38
# Similarly for members columns: members_0, members_1, ..., members_38

# Coalesce genre columns: pick first non-null genre among genre_0 ... genre_38
genre_cols = [f"genre_{i}" for i in range(len(dfs))]
df_joined["genre"] = df_joined[genre_cols].bfill(axis=1).iloc[:, 0]

# Sum all members columns (members_0 ... members_38), ignoring NaNs
members_cols = [f"members_{i}" for i in range(len(dfs))]
df_joined["members"] = df_joined[members_cols].fillna(0).sum(axis=1).astype(int)

# Now group by genre and sum members
df_result = df_joined.groupby("genre", dropna=False, as_index=False)["members"].sum()

# Write output with exact target schema and column names
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_76/target_multisource_mcts.csv", index=False)