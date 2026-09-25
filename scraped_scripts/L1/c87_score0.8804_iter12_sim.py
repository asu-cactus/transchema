import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

agg = df0.groupby("condition").agg({"click": ["min", "max"]})
agg.columns = ["click_min", "click_max"]
agg = agg.reset_index()

agg["click"] = (agg["click_min"] + agg["click_max"]) / 2
result = agg[["condition", "click"]]

result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)