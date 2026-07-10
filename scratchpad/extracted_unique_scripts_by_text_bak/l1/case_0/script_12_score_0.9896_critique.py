import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)

# Clean 'State' column: strip whitespace and drop rows with missing State or AverageTemperature
df0 = df0.dropna(subset=["State", "AverageTemperature"])
df0["State"] = df0["State"].str.strip()

result = df0.groupby("State", as_index=False)["AverageTemperature"].mean()
result.columns = ["State", "AverageTemperature"]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)