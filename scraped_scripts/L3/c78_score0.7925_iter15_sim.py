import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_78/training_2.csv", index_col=0)

merged_0_1 = pd.merge(source0, source1, on="user_id", how="inner")

count_df = merged_0_1.groupby(["movie_id", "sex"]).size().reset_index(name="count")

pivot_df = count_df.pivot(index="movie_id", columns="sex", values="count").reset_index()

result = pd.merge(pivot_df, source2[["movie_id", "title"]], on="movie_id", how="inner")

result = result.rename(columns={"F": "F", "M": "M"})

result = result[["movie_id", "title", "F", "M"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_78/target_multisource_mcts.csv", index=False)