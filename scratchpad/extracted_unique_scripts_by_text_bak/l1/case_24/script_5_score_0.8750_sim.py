import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)

joined = pd.merge(source0, source0, on="condition")

result = joined.groupby("condition", as_index=False)["click_x"].sum()
result.columns = ["condition", "click"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)