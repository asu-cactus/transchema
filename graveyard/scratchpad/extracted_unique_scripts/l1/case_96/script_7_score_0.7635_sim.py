import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

agg = df0.groupby("Publisher", dropna=False)[["Height", "Weight"]].sum().reset_index()

agg["Publisher"] = agg["Publisher"].astype('category').cat.codes

agg = agg[["Publisher"]]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)