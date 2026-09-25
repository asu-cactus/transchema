import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)
result = df0[['sex', 'smoker', 'tip_pct']]
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)