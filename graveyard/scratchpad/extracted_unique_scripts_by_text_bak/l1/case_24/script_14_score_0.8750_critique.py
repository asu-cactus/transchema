import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_24/training_0.csv", index_col=0)
df0 = df0.astype({"condition": int, "click": int})

# Group by 'condition' and sum 'click'
result = df0.groupby("condition", as_index=False).agg({"click": "sum"})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_24/target_multisource_mcts.csv", index=False)