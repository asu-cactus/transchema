import pandas as pd

df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)
result = df9.groupby("KEYWORDS_NUM", as_index=False).size().rename(columns={"size": "KEYWORDS_NUM"})
result = result[["KEYWORDS_NUM"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)