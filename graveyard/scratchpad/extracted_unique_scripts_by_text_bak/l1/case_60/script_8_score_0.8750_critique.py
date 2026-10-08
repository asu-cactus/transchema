import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_60/training_0.csv", index_col=0)
filtered = df0[df0["type"] == "Urban"]
agg_sum = filtered["driver_count"].sum()
result = pd.DataFrame({"type": ["Urban"], "driver_count": [int(agg_sum)]})
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts.csv", index=False)