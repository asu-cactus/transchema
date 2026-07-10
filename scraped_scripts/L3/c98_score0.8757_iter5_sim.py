import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_98/training_1.csv", index_col=0)

result = df0.groupby("MOTATE_V", dropna=False).agg(count=("CLUES", "count")).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_98/target_multisource_mcts.csv", index=False)