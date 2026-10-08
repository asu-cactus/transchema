import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_77/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_77/training_1.csv", index_col=0)

grouped_source0 = source0.groupby("school_name", as_index=False)["reading_score"].sum()

joined = pd.merge(grouped_source0, source1, on="school_name", how="inner")

result = joined[["school_name", "reading_score"]].copy()
result["reading_score"] = result["reading_score"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_77/target_multisource_mcts.csv", index=False)