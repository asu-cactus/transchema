import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv", index_col=0)
agg = df0.groupby("customer_id", as_index=False).agg({"date": "max"})
agg["date"] = agg["date"].astype(str)
agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv", index=False)