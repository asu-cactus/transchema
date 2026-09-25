import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_55/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_55/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_55/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df1, df0, on="movieId")

result = merged[["movieId", "title", "genres", "userId", "rating"]].copy()
result["movieId"] = result["movieId"].astype(int)
result["title"] = result["title"].astype(str)
result["genres"] = result["genres"].astype(str)
result["userId"] = result["userId"].astype(float)
result["rating"] = result["rating"].astype(float)

result.to_csv(target_path, index=False)