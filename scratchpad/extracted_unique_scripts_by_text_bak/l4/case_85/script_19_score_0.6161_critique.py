import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

# Group by 'crit_cn' and count distinct 'critic'
agg = df0.groupby("crit_cn", as_index=False).agg({"critic": pd.Series.nunique})

agg["critic"] = agg["critic"].astype(int)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)