import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_23/training_1.csv", index_col=0)

grouped = source0.groupby("city", as_index=False)["fare"].sum()

joined = pd.merge(source1, grouped, how="inner", on="city")

joined["type"] = joined["type"].astype('category').cat.codes

result = joined[["city", "type"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_23/target_multisource_mcts.csv", index=False)