import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_22/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="school_name", how="inner")
result = merged[["school_name", "math_score"]].copy()
result["math_score"] = result["math_score"].astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_22/target_multisource_mcts.csv", index=False)