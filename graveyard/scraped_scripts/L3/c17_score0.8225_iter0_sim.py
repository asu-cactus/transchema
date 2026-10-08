import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_2.csv", index_col=0)

merged_0_2 = pd.merge(source0, source2, on="user_id", how="inner")
merged_all = pd.merge(merged_0_2, source1, on="movie_id", how="inner")

grouped = merged_all.groupby(["title", "gender"])["rating"].mean().reset_index()

pivot = grouped.pivot(index="title", columns="gender", values="rating").reset_index()
pivot.columns.name = None
pivot = pivot.rename(columns={"F": "F", "M": "M", "title": "title"})

pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_17/target_multisource_mcts.csv", index=False)