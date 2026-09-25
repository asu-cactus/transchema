import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)
df = df[df["Country"] == "Russia"]
result = df.groupby("State", as_index=False)["AverageTemperature"].mean()
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)