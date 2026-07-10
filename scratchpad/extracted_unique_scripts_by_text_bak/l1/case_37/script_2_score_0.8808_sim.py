import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_37/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_37/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on=["business_id", "date"], how="inner")

result = merged[["business_id", "Score", "date", "type", "ViolationTypeID", "risk_category", "description"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_37/target_multisource_mcts.csv", index=False)