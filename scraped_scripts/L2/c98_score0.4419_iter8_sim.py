import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_98/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_98/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_98/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

merged = pd.merge(df1, df0, on="city", how="inner")
result = merged[["city", "fare"]]

result.to_csv(target_path, index=False)