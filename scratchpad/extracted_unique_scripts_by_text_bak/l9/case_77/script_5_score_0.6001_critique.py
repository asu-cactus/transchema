import pandas as pd

# List all source file paths
source_files = [
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

# Read and union all source tables
dfs = [pd.read_csv(f, index_col=0) for f in source_files]
df_all = pd.concat(dfs, ignore_index=True)

# Group by anime_id and aggregate
# For string columns: take first
# For episodes and members: take max (integer counts)
# For rating: take mean (float)
agg_dict = {
    "name": "first",
    "genre": "first",
    "type": "first",
    "episodes": "max",
    "rating": "mean",
    "members": "max",
}

df_result = df_all.groupby("anime_id", as_index=False).agg(agg_dict)

# Ensure column order matches target schema
df_result = df_result[
    ["anime_id", "name", "genre", "type", "episodes", "rating", "members"]
]

# Write output
df_result.to_csv(
    "autopipeline-benchmarks/github-pipelines/length9_77/target_multisource_mcts.csv",
    index=False,
)