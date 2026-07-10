import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv", index_col=0)

agg = df0.groupby("condition")["click"].sum().reset_index()

result = agg.astype({"condition": int, "click": int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)