import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_77/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_77/training_1.csv", index_col=0)

joined = pd.merge(source0, source1, on="school_name", how="inner")

result = joined.groupby("school_name", as_index=False).agg({"size": "max"})

result = result.rename(columns={"size": "reading_score"})

result["reading_score"] = result["reading_score"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_77/target_multisource_mcts.csv", index=False)