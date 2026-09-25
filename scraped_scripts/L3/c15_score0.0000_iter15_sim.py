import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_15/training_2.csv", index_col=0)

s1_renamed = s1.rename(columns={"user_id": "user_id", "gender": "gender"})
s2_renamed = s2.rename(columns={"user_id": "user_id", "movie_id": "movie_id", "rating": "rating", "timestamp": "timestamp"})

union_result = pd.concat([s1_renamed, s2_renamed], axis=0, ignore_index=True, sort=False)

joined = pd.merge(union_result, s0, on="movie_id", how="inner")

pivot_df = joined.pivot_table(index=["title"], columns="gender", values="rating", aggfunc="mean")

pivot_df = pivot_df.rename(columns={"F": "F", "M": "M"})

result = pivot_df.reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_15/target_multisource_mcts.csv", index=False)