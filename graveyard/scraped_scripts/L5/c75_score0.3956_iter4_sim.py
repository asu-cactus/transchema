import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_0.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_3.csv", index_col=0)

merged = pd.merge(source0, source3, left_on="Ord_id", right_on="Ord_id")

result = merged.groupby("Ord_id", as_index=False).agg({"Profit": "sum"})

result = result[["Profit"]].astype({"Profit": float})

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_75/target_multisource_mcts.csv", index=False)