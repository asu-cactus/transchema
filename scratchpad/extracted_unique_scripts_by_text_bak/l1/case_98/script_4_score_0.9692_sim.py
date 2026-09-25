import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

merged = pd.merge(source0, source1, left_on="right_index", right_index=True, how="inner")

result = merged.rename(columns={"0_x": "0_x", "0_y": "0_y"})
result = result[["0_x", "0_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv")