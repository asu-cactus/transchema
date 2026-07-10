import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_96/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, left_on="Publisher", right_on="hero_names")
result = merged.groupby("Publisher", as_index=False).size().rename(columns={"size": "Publisher"})
result = result[["Publisher"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv", index=False)