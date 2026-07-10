import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_29/training_0.csv", index_col=0)

result = df0.groupby("Gender", dropna=False).agg({"SN": "count"}).rename(columns={"SN": "0"}).reset_index()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_29/target_multisource_mcts.csv", index=False)