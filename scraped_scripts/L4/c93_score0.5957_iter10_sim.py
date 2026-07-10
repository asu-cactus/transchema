import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_93/training_2.csv", index_col=0)

union_result = source0.copy()

join_result_1 = pd.merge(union_result, source2, on="user_id", how="inner")

join_result_2 = pd.merge(join_result_1, source1, on="movie_id", how="inner")

join_result_2["gender"] = join_result_2["gender"].map({"M": 1, "F": 2}).astype("Int64")
join_result_2["age"] = pd.to_numeric(join_result_2["age"], errors="coerce").astype("Int64")
join_result_2["zip"] = join_result_2["zip"].str.extract(r"(\d+)").astype("Int64")

join_result_2["title_x"] = join_result_2["title_x"] = join_result_2["title"].factorize()[0] + 1
join_result_2["genres_x"] = join_result_2["genres"].factorize()[0] + 1

result = join_result_2.rename(columns={
    "title_x": "title_x",
    "genres_x": "genres_x",
    "title": "title_y",
    "genres": "genres_y"
})[["movie_id", "user_id", "rating", "timestamp", "gender", "age", "occupation", "zip", "title_x", "genres_x", "title_y", "genres_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_93/target_multisource_mcts.csv", index=False)