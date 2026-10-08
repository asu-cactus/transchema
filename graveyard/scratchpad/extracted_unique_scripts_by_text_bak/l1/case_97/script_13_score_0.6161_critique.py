import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

result = df.groupby("crit_cn", as_index=False).agg({"critic": pd.Series.nunique})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)