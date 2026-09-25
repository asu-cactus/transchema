import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)

joined = pd.merge(df, df, on="Country")

result = joined.groupby("State", as_index=False)["AverageTemperature_x"].mean()
result.columns = ["State", "AverageTemperature"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)