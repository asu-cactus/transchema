import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)

agg_df = df0.groupby("condition").agg({"click": ["min", "max"]})
agg_df.columns = ["click_min", "click_max"]
agg_df = agg_df.reset_index()

agg_df["click"] = agg_df[["click_min", "click_max"]].max(axis=1)
result = agg_df[["condition", "click"]].astype({"condition": int, "click": int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)