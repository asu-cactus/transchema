import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv", index_col=0)

grouped = df0.groupby("condition").agg({"click": ["sum", "count"]})
grouped.columns = grouped.columns.droplevel(0)
grouped = grouped.reset_index()

grouped.rename(columns={"sum": "0"}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)