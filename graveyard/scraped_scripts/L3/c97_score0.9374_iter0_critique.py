import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_97/training_2.csv", index_col=0)

# Join Source1 and Source2 on 'user id'
user_ratings = pd.merge(source1, source2, how="inner", left_on="user id", right_on="user id")

# Join the above with Source0 on 'movie id'
full_data = pd.merge(user_ratings, source0, how="inner", left_on="movie id", right_on="movie id")

# Group by 'movie title' and aggregate mean rating
result = full_data.groupby("movie title", as_index=False)["rating"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_97/target_multisource_mcts.csv", index=False)