import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_3/training_0.csv", index_col=0)

joined = pd.merge(source0, source0, on="Major_category")

result = joined.groupby("Major_category", as_index=False)["Median_x"].mean()
result.columns = ["Major_category", "Median"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_3/target_multisource_mcts.csv", index=False)