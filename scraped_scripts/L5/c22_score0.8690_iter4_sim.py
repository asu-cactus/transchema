import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_22/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_22/training_1.csv", index_col=0)

merged = pd.merge(df1, df0, on="school_name")

result = merged.groupby("school_name", as_index=False)["math_score"].mean()
result["math_score"] = result["math_score"].round().astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_22/target_multisource_mcts.csv", index=False)