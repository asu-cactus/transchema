import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_24/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="movie_id", how="left")

result = merged.groupby("title").agg(size=("user_id", "count"), mean=("rating", "mean")).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_24/target_multisource_mcts.csv", index=False)