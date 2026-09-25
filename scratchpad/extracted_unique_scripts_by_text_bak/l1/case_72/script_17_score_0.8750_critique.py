import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv", index_col=0)

filtered = df[df["click"] == 0]

grouped = filtered.groupby("condition", as_index=False).agg({"click": "count"})

grouped = grouped.rename(columns={"click": "0"})

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv", index=False)