import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)

# Clean 'State' column by stripping whitespace
df0["State"] = df0["State"].str.strip()

# Group by cleaned 'State' and compute mean of 'AverageTemperature'
result = df0.groupby("State", as_index=False)["AverageTemperature"].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)