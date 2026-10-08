import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)

agg_df = df0.groupby("condition", as_index=False).agg({"click": "sum"})

result = agg_df.astype({"condition": int, "click": int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)