import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_17/training_2.csv", index_col=0)

merged_0_1 = pd.merge(source0, source1, on="movie_id", how="inner")
merged_all = pd.merge(merged_0_1, source2, on="user_id", how="inner")

grouped = merged_all.groupby(["title", "gender"]).agg(user_count=("user_id", "count")).reset_index()

pivoted = grouped.pivot(index="title", columns="gender", values="user_count").fillna(0)

pivoted = pivoted.rename(columns={"F": "F", "M": "M"}).reset_index()

pivoted["F"] = pivoted["F"].astype(float)
pivoted["M"] = pivoted["M"].astype(float)

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length3_17/target_multisource_mcts.csv", index=False)