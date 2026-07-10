import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

grouped = df0.groupby("crit_cn", as_index=False)["critic"].count()
grouped = grouped.rename(columns={"critic": "critic"})

# The target schema requires 'critic' as integer, but the count aggregation returns int64, which is fine.
# The 'critic' column in target examples looks like a count of critics per crit_cn, so count aggregation is correct.

grouped["critic"] = grouped["critic"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)