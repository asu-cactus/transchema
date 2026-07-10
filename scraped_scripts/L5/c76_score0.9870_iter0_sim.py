import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_76/training_1.csv", index_col=0)

result = df1.groupby("school_name", as_index=False)["reading_score"].mean()
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_76/target_multisource_mcts.csv", index=False)