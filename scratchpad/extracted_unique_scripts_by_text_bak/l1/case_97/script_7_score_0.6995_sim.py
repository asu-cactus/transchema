import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
grouped = union_df.groupby("crit_cn", as_index=False)["critic"].count()
grouped = grouped.rename(columns={"critic": "critic"})
grouped["critic"] = grouped["critic"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)