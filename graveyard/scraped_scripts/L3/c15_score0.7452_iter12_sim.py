import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_2.csv", index_col=0)

joined_0 = pd.merge(source2, source1, on="user_id")
joined_1 = pd.merge(joined_0, source0, on="movie_id")

f_ratings = joined_1[joined_1["gender"] == "F"].groupby("title")["rating"].mean()
m_ratings = joined_1[joined_1["gender"] == "M"].groupby("title")["rating"].mean()

result = pd.DataFrame({
    "title": f_ratings.index,
    "F": f_ratings.values,
    "M": m_ratings.reindex(f_ratings.index).values
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_15/target_multisource_mcts.csv", index=False)