import pandas as pd

# Read all source tables (assuming the naming pattern and locations)
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_2.csv", index_col=0)

# Union all source tables
df = pd.concat([df0, df1, df2], ignore_index=True)

# Group by State and compute mean AverageTemperature
result = df.groupby("State", as_index=False)["AverageTemperature"].mean()

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)