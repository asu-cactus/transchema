import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_8/training_0.csv", index_col=0)

result = df0.groupby("school_name", as_index=False)["math_score"].sum()
result["math_score"] = result["math_score"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_8/target_multisource_mcts.csv", index=False)