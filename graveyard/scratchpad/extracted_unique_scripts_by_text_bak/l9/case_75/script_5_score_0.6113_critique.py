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

# Ensure correct dtypes
df = df.astype({
    "anime_id": "Int64",
    "name": "string",
    "genre": "string",
    "type": "string",
    "episodes": "Int64",
    "rating": "float64",
    "members": "Int64"
})

# Define aggregation functions
def first_non_null(series):
    return series.dropna().iloc[0] if not series.dropna().empty else pd.NA

agg_dict = {
    "genre": first_non_null,
    "rating": "mean",
    "members": "max"
}

group_cols = ["anime_id", "name", "type", "episodes"]

df_grouped = df.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()

# Cast members back to Int64 (max aggregation may produce float)
df_grouped["members"] = df_grouped["members"].astype("Int64")

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_75/target_multisource_mcts.csv", index=False)