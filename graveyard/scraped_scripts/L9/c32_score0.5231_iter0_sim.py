import pandas as pd

df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
result = df1.groupby("VISITS_NUM", as_index=False).size().rename(columns={"size": "count"})
result = result[["VISITS_NUM"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)