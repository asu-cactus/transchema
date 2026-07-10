import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

joined = pd.merge(source0, source0, left_on="neighbourhood", right_on="neighbourhood")

result = joined[["neighbourhood", "price_x"]].copy()
result.rename(columns={"price_x": "price_24"}, inplace=True)
result["price_24"] = result["price_24"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)