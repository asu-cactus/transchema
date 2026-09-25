import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

result = df0.groupby("crit_cn", as_index=False)["critic"].count()
result = result.rename(columns={"critic": "critic"})
result["critic"] = result["critic"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)