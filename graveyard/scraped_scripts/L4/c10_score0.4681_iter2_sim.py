import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_10/training_2.csv", index_col=0)

join_01 = pd.merge(source0, source1, on="user_id", how="inner")
join_result = pd.merge(join_01, source2, on="movie_id", how="inner")

join_result = join_result.rename(columns={
    "movie_title": "movie_title_y",
    "year": "year_y"
})

join_result["movie_title_x"] = join_result["movie_title_y"].astype('category').cat.codes
join_result["year_x"] = pd.to_numeric(join_result["year_y"], errors='coerce').fillna(0).astype(int)

join_result["age"] = pd.to_numeric(join_result["age"], errors='coerce').fillna(0).astype(int)
join_result["gender"] = join_result["gender"].map({"M": 1, "F": 2}).fillna(0).astype(int)
join_result["occupation"] = pd.to_numeric(join_result["occupation"], errors='coerce').fillna(0).astype(int)
join_result["zip"] = pd.to_numeric(join_result["zip"], errors='coerce').fillna(0).astype(int)
join_result["user_id"] = pd.to_numeric(join_result["user_id"], errors='coerce').fillna(0).astype(int)
join_result["rating"] = pd.to_numeric(join_result["rating"], errors='coerce').fillna(0).astype(int)
join_result["timestamp"] = pd.to_numeric(join_result["timestamp"], errors='coerce').fillna(0).astype(int)

final_cols = ['movie_id', 'movie_title_x', 'year_x', 'user_id', 'rating', 'timestamp', 'age', 'gender', 'occupation', 'zip', 'movie_title_y', 'year_y']
result = join_result[final_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_10/target_multisource_mcts.csv", index=False)