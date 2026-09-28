import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_1.csv", index_col=0)

groupby_result = df1.groupby("city", as_index=False)["fare"].mean()

result = pd.merge(df0, groupby_result, on="city", how="inner")

final = result[["city", "type", "fare"]]
final.to_csv("autopipeline-benchmarks/github-pipelines/length3_69/target_multisource_mcts.csv", index=False)