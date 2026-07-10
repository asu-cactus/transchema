import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv"
source0_copy_path = "autopipeline-benchmarks/github-pipelines/length4_99/training_0.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df0_copy = pd.read_csv(source0_copy_path, index_col=0)

merged = pd.merge(df0, df0_copy, on="PassengerId", suffixes=('_x', '_y'))

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_99/target_multisource_mcts.csv", index=False)