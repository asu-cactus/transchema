import pandas as pd

files = [
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

# Read all sources
dfs = [pd.read_csv(f, index_col=0) for f in files]

# UNION all sources
df = pd.concat(dfs, ignore_index=True)

# Drop duplicates on anime_id and genre to avoid double counting members for same anime-genre pair
df = df.drop_duplicates(subset=['anime_id', 'genre'])

# Group by genre and sum members
result = df.groupby("genre", as_index=False)["members"].sum()

# Ensure correct types
result["genre"] = result["genre"].astype(str)
result["members"] = result["members"].astype(int)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_76/target_multisource_mcts.csv", index=False)