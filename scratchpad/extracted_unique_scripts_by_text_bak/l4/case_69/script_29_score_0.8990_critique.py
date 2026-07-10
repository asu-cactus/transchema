import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

# LEFT join to preserve all rows from df0
df01 = pd.merge(df0, df1, on="user_id", how="left")
result = pd.merge(df01, df2, on="user_id", how="left")

# Group by the leftmost columns that are unique and non-float
grouped = result.groupby(["user_id", "year_school", "floor"], as_index=False).agg({
    "party": "first",
    "libcon": "first",
    "fav_music": "first"
})

# Reorder columns to match target schema exactly
grouped = grouped[["user_id", "year_school", "floor", "party", "libcon", "fav_music"]]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)