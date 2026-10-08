import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_24/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_24/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_24/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

df_merged = df0.merge(df1, on="movie_id", how="inner")

grouped = df_merged.groupby("title").agg(
    size=("rating", "count"),
    mean=("rating", "mean")
).reset_index()

grouped["size"] = grouped["size"].astype(int)
grouped["mean"] = grouped["mean"].astype(float)

grouped.to_csv(target_path, index=False)