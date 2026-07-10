import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="condition")

result = joined.groupby("condition", as_index=False)["click_x"].sum()
result.columns = ["condition", "click"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv", index=False)