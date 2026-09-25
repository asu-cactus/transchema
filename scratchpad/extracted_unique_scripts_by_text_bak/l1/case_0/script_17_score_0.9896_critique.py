import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv"
df = pd.read_csv(source_path, index_col=0)

result = df.groupby("State", as_index=False)["AverageTemperature"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)