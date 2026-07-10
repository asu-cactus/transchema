import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_31/training_2.csv", index_col=0)

join_1 = pd.merge(source2, source1, on="user_id")
join_2 = pd.merge(join_1, source0, on="movie_id")

pivot = join_2.pivot_table(index="title", columns="gender", values="rating", aggfunc="mean")

pivot = pivot.fillna(0)

result = pivot.reset_index()

result = result[["title", "F", "M"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_31/target_multisource_mcts.csv", index=False)