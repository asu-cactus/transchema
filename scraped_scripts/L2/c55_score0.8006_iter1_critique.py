import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_55/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_55/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, on="movieId")

# Group by movieId, title, genres
grouped = merged.groupby(["movieId", "title", "genres"], as_index=False).agg(
    userId=pd.NamedAgg(column="userId", aggfunc=lambda x: x.nunique()),
    rating=pd.NamedAgg(column="rating", aggfunc="mean")
)

# Cast columns to target types
grouped["movieId"] = grouped["movieId"].astype(int)
grouped["title"] = grouped["title"].astype(str)
grouped["genres"] = grouped["genres"].astype(str)
grouped["userId"] = grouped["userId"].astype(float)
grouped["rating"] = grouped["rating"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length2_55/target_multisource_mcts.csv", index=False)