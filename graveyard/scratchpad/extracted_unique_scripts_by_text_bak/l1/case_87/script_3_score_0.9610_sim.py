import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

grouped = df0.groupby("condition").agg(click_count=("click", "count"), click_avg=("click", "mean")).reset_index()

result = grouped[["condition", "click_avg"]].rename(columns={"click_avg": "click"})
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)