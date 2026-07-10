import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

result = df0.groupby("crit_cn", as_index=False).agg({"critic": pd.Series.nunique})

result = result.rename(columns={"critic": "critic", "crit_cn": "crit_cn"})

result["critic"] = result["critic"].astype(int)
result["crit_cn"] = result["crit_cn"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)