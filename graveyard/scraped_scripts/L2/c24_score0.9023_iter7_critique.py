import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_24/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_24/training_1.csv", index_col=0)

joined = pd.merge(df1, df0, on="movie_id", how="left")

agg = joined.groupby("title").rating.agg(size="count", mean="mean").reset_index()

agg["title"] = agg["title"].astype(str)
agg["size"] = agg["size"].astype(int)
agg["mean"] = agg["mean"].fillna(0).astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length2_24/target_multisource_mcts.csv", index=False)