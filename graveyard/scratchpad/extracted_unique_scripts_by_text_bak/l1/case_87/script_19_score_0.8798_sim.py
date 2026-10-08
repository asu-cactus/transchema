import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_87/training_0.csv", index_col=0)

agg_df = df0.groupby("condition").agg(click_max=("click", "max"), click_min=("click", "min")).reset_index()
agg_df["click"] = (agg_df["click_max"] + agg_df["click_min"]) / 2
result = agg_df[["condition", "click"]]
result["condition"] = result["condition"].astype(int)
result["click"] = result["click"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_87/target_multisource_mcts.csv", index=False)