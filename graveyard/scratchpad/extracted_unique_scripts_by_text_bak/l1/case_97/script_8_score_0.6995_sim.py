import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)
grouped = df0.groupby("crit_cn", as_index=False).agg(critic=("critic", "count"))
grouped["critic"] = grouped["critic"].astype(int)
grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)